import yaml
import re

from ldap3 import Server, Connection, SUBTREE, SIMPLE, SYNC, ALL, SASL, NTLM, MODIFY_REPLACE

# define the server and the connection
def connect_toldap(server,username,password):
    srv = Server(server, port = 636, use_ssl = True, get_info=ALL)
    conn = Connection(srv, user=username, password=password, authentication=NTLM)
    if conn.bind() is None:
        print('Error in bind:', conn.result['description'])
        return None # todo raise error with exception from conn.result
    print('LDAP connect result:', conn.result['description'])
    return conn
    

def get_computer_suffix(
     instance_id: str,
     last_nletters: int = 8 
)->str:
    """
    Method converts EC2 instance ID into hostname suffix and returns it
    :param instance_id: EC2 instance ID retrieved from termination event, e.g. i-1234567890abcdef0
    :param last_nletters: Computer suffix name is in domain join process created top of last 8 letters
    """
    if not is_valid_id(instance_id):
        return None
    instance_id_len = len(instance_id)
    computer_suffix = instance_id[instance_id_len-last_nletters:instance_id_len] 
    return computer_suffix

def search_computer(conn,search_base,instance_id)->str:
    if not is_valid_id(instance_id):
        return None
    object_class = 'computer'
    computer_suffix = get_computer_suffix(instance_id)
    other_telephone = instance_id
    search_filter = f'(&(objectClass={object_class})(|(CN=*{computer_suffix})(OtherTelephone={other_telephone})))'
    conn.search(search_base,
            search_filter = search_filter,
            search_scope = SUBTREE,
            attributes = ['cn', 'distinguishedName','OtherTelephone'],
            size_limit = 2) # search for more than 1 occurance suffix, if found then raise error
    
    search_response = [entry for entry in conn.response if entry['type'] in 'searchResEntry']

    if not search_response:
        print(f'Computer with suffix \'{computer_suffix}\' was not found in ldap directory')
        return None
    if len(search_response) > 1 :
        raise NameError(f'Ambiguity - multiple computers with suffix {computer_suffix} found!!!')

    computer_dn = search_response[0]['dn']
    print(f'Computer with suffix {computer_suffix} succesfully found. Returning {computer_dn}')
    return computer_dn

def delete_computer(conn,dn: str):
    # todo - add validation for DN
    print("Deleting: ", dn)
    print(type(conn.delete(dn)))
    print(conn)
   # print(delete_result['description'])
    # if delete_result['description'] in 'success':
    #    print(f'Deleted: {dn}')

def create_computer(conn,dn):
    object_class = ['computer']
    conn.add(dn, object_class, {'userAccountControl':'544'})

def is_valid_id(instance_id) ->bool:
    m = re.match(r"^i-[a-z0-9A-Z]{17}$", instance_id)
    if m is None:
        print(f'Instance ID {instance_id} is in wrong format')
        return False
    print(f'Instance ID {m.group()} is in correct format')
    return True

result = is_valid_id("i-1234567890abcdef0")
if(result):
    print('Only positive news :)')

def disable_computer(conn,dn: str):
    print("disabling computer")
    disable_account = '546'
    description_msg = 'Disabled by AWS Lambda on termination event'
    changes = {'userAccountControl':[MODIFY_REPLACE,[disable_account]], 'description':[MODIFY_REPLACE,[description_msg]]}

    conn.modify(dn,changes)
    print(conn.result)

def rename_computer(conn,dn):
    print("renaming computer")

def move_computer(conn,dn):
    print("moved computer")



config      = yaml.safe_load(open(".config.yml"))
server      = config['server']
username    = config['username']
password    = config['password']
search_base = config['search_base']
instance_id = config['computer_name']
computer_dn = config['computer_dn']


# scenario 1 - computer does not exist in ldap
## instance_id = 'asdf'

# scenario 2 - exactly one computer exists with given name (CN) 

# scenario 3 - multiple computers exists with the same suffix but different fullname/CN (active directory doesn't support computer object with the same CN)

# scenario 4 - ldap connection credentials are wrong

# scenario 5 - wrong ldap server URL (or ldap unavailable)

# scenario 6 - wronge tcp port 636 (or ldap unavailable)


conn = connect_toldap(server,username,password)
if conn is not None:
    create_computer(conn,computer_dn)
    #disable_computer(conn,computer_dn)
    search_result = search_computer(conn,search_base,instance_id)
    if search_result is not None:
        delete_computer(conn,search_result)

# close the connection
conn.unbind()

