import yaml
from ldap3 import Server, Connection, SUBTREE, SIMPLE, SYNC, ALL, SASL, NTLM

# load parameters
import yaml
config = yaml.safe_load(open(".config.yml"))

# define the server and the connection
s = Server(config['server'], get_info=ALL)
c = Connection(s, user=config['username'], password=config['password'], authentication=NTLM)
# perform the Bind operation
if not c.bind():
    print('error in bind', c.result)
else:
    print('connection is succesfull', c.result)

c.search(search_base = config['search_base'],
         search_filter = '(&(objectClass=computer)(CN={}))'.format(config['computer_name']),
         search_scope = SUBTREE,
         attributes = ['cn', 'distinguishedName'],
         paged_size = 1)

for entry in c.response:
    if entry['type'] == 'searchResEntry':
        print(entry)

