from keepassxc_browser import Connection, Identity, ProtocolError
from pathlib import Path

def main():
    client_id = 'python-keepassxc-browser'

    state_file = Path('.assoc')
    if state_file.exists():
        with state_file.open('r') as f:
            data = f.read()
        id = Identity.unserialize(client_id, data)
    else:
        id = Identity(client_id)

    c = Connection()
    c.connect()
    c.change_public_keys(id)
    try:
        c.get_database_hash(id)
    except ProtocolError as ex:
        print(ex)
        exit(1)

    if not c.test_associate(id):
        associated_name = c.associate(id)
        assert c.test_associate(id)
        data = id.serialize()
        with state_file.open('w') as f:
            f.write(data)
        del data

    c.create_password(id)
    groups = c.get_database_groups(id)
    root = groups[0] # {name: 'AAAA', uuid: 'BBBB', children: [...]}
    
    # groups on root level are good
    easy_foo = c.create_database_group(id, 'foo')
    assert easy_foo['uuid'] == c.find_group_uuid(id, 'foo')

    # groups on any level are good too
    hard_foo = c.create_database_group(id, 'foo/bar/baz')
    assert hard_foo['uuid'] == c.find_group_uuid(id, 'foo/bar/baz')

    # this method can not find root, because it search on top of it
    assert c.find_group_uuid(id, root['name']) is None
    
    c.set_login(id, 
                url='https://python-test123', 
                login='test-user', 
                password='test-password', 
                group_uuid=hard_foo['uuid'], 
                submit_url=None)
    
    c.get_logins(id, url='https://python-test123')
    # c.lock_database(id)
    c.disconnect()

if __name__ == "__main__":
    main()
