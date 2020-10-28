import yaml
import re

from ldap3 import Server, Connection, SUBTREE, SIMPLE, SYNC, ALL, SASL, NTLM, MODIFY_REPLACE

# define the server and the connection
def connect_toldap(server,username,password):
    srv = Server(server, port = 636, use_ssl = True, get_info=ALL)
    print('INFO - REQ_CONN_LDAP: {}'.format(srv))
    conn = Connection(srv, user=username, password=password, authentication=NTLM)
    conn.bind()
    if conn.result['result'] != 0:
        raise NameError('ERROR - LDAP connection failed with message \'{}\''.format(conn.result['description']))
    print('INFO - RES_CONN_LDAP: {}'.format(conn.result))
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
    print('INFO - REQ_SEARCH_COMPUTER: {}'.format(search_filter))
    conn.search(search_base,
            search_filter = search_filter,
            search_scope = SUBTREE,
            attributes = ['cn', 'distinguishedName','OtherTelephone'],
            size_limit = 2) # on purpose more than 1 in order to check unambiguity of computer objects
    search_response = [entry for entry in conn.response if entry['type'] in 'searchResEntry']

    if not search_response:
        print(f'WARN - RES_SEARCH_COMPUTER: NOT FOUND')
        return None
    if len(search_response) > 1 :
        raise NameError(f'Error - computer ambiguity returned by filter \'{search_filter}\'')

    computer_dn = search_response[0]['dn']
    is_valid_dn(computer_dn) # if not valid raise exception
    print(f'INFO - RES_SEARCH_COMPUTER: found {computer_dn}')
    return computer_dn

def delete_computer(conn,dn: str):
    print(f'INFO - REQ_DELETE_COMPUTER: {dn}')
    is_valid_dn(dn)
    conn.delete(dn)
    if conn.result['result'] == 0:
        print('INFO - RES_DELETE_COMPUTER: {}'.format(conn.result['description']))
        return True
    else:
        raise NameError('Error - Removal of {} failed with reason {}'.format(dn,conn.result['description']))

def create_computer(conn,dn):
    object_class = ['computer']
    print(f'INFO - REQ_CREATE_COMPUTER: {dn}')
    conn.add(dn, object_class, {'userAccountControl':'544'})
    print('INFO - RES_CREATE_COMPUTER: {} '.format(conn.result['description']))


def is_valid_id(instance_id) ->bool:
    m = re.match(r"^i-[a-z0-9A-Z]{17}$", instance_id)
    if m is None:
        raise NameError(f'Instance ID \'{instance_id}\' is in wrong format')
    return True

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

def is_valid_dn(dn):
    """
    Method validates active directory computer object name where standard name contains only 
    letters (a-zA-Z), number (0-9), and hyphens (-). No spaces, no dots (.). Max length is 63 characters.
    :param dn: distinguished name format
    """
    m = re.match(r"^CN=[a-zA-Z0-9-]{1,63},(.*)", dn)
    if m is None:
        raise NameError(f'DN \'{dn}\' is in wrong format')
    print(f'DN {dn} is correct format')
    return True



if __name__ == '__main__':
    config      = yaml.safe_load(open(".config.yml"))
    server      = config['server']
    username    = config['username']
    password    = config['password']
    password_wrong = config['password_wrong']
    search_base = config['search_base']
    instance_id = config['instance_id']
    computer_dn = config['computer_dn']
    computer_dn2 = config['computer_dn2']
    computer_dn_wrong = config['computer_dn_wrong']
    # scenarion 0 - start ldap connection
    conn = connect_toldap(server,username,password)

    # scenario 1 - computer does not exist in ldap
    # scenario 2 - exactly one computer exists with given name (CN) 
    ##create_computer(conn,computer_dn)

    # scenario 3 - multiple computers exists with the same suffix but different fullname/CN (active directory doesn't support computer object with the same CN)
    ##create_computer(conn,computer_dn)
    ##create_computer(conn,computer_dn2)
    # scenario 4 - ldap connection credentials are wrong
    ##conn = connect_toldap(server,username,password_wrong)
    # scenario 5 - wrong ldap server URL (or ldap unavailable)

    # scenario 6 - wrong tcp port 636 (or ldap unavailable)

    # scenario 7 - disable computer
    ##disable_computer(conn,computer_dn)

    # scenario 8 - check dn
    is_valid_dn(computer_dn)
    is_valid_dn(computer_dn2)
    is_valid_dn(computer_dn_wrong)


    if conn is not None:
        search_result = search_computer(conn,search_base,instance_id)
        if search_result is not None:
            delete_computer(conn,search_result)

    # close the connection
    conn.unbind()
