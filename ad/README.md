### Install Ldap
```
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
```
```
pip3 install python-ldap
```

### better is to use ldap 3
- https://pypi.org/project/ldap3/

```
python -m pip install ldap3
```

### Ldap3 reference
- https://www.python-ldap.org/en/python-ldap-3.3.0/reference/ldap.html#example
- https://ldap3.readthedocs.io/en/latest/searches.html

### SQS - challenges in message batch processing

```
https://awslabs.github.io/aws-lambda-powertools-python/utilities/batch/#processing-messages-from-sqs
```
```
https://github.com/awslabs/aws-lambda-powertools-python/issues/92
```

```
https://medium.com/@brettandrews/handling-sqs-partial-batch-failures-in-aws-lambda-d9d6940a17aa
```
