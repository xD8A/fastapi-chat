
Create database
```bash
sqlite3 app.db < schema.sql
```
Create users
```bash
sqlite3 app.db \
"INSERT INTO users (name, email, password_hash)"\
" VALUES ('admin', 'admin@example.com', '"\
`python3 -c 'import bcrypt;print(bcrypt.hashpw(b"password", bcrypt.gensalt()).decode())'`\
"');"\
"INSERT INTO users (name, email, password_hash)"\
" VALUES ('user', 'user@example.com', '"\
`python3 -c 'import bcrypt;print(bcrypt.hashpw(b"password", bcrypt.gensalt()).decode())'`\
"');"
```

Add contacts
```bash
JWT_TOKEN=`curl -s -H "Content-Type: application/json" \
  -X POST \
  -d '{"name":"admin","password":"password"}' \
  http://localhost:8000/sign-in \
| python3 -c "import sys, json; print(json.load(sys.stdin)['token'])"` \
&& curl -i -H "Content-Type: application/json" -H "Authorization: Bearer $JWT_TOKEN" \
  -X POST \
  -d '{"friend":{"id":2},"name":"user"}' \
  http://localhost:8000/contacts
JWT_TOKEN=`curl -s -H "Content-Type: application/json" \
  -X POST \
  -d '{"name":"user","password":"password"}' \
  http://localhost:8000/sign-in \
| python3 -c "import sys, json; print(json.load(sys.stdin)['token'])"` \
&& curl -i -H "Content-Type: application/json" -H "Authorization: Bearer $JWT_TOKEN" \
  -X POST \
  -d '{"friend":{"id":1},"name":"admin"}' \
  http://localhost:8000/contacts
```