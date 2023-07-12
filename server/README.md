# highorder server

## deploy

```
python setup.py bdist_wheel

pex  -f dist/ rich highorder -m highorder -o ./dist/highorder.pex

scp dist/highorder.pex ubuntu@server_or_ip:/home/ubuntu/service/

```