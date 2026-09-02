#!/bin/sh

echo "Inyección SQL"
c="curl -s "'"'"localhost:8080/movies/'%20OR%201=1%20--/stats"'"'""
echo "$c"
bash -c "$c | jq"

sleep 5

echo
echo
echo "Sin credenciales"
c="curl -s 'localhost:8080/users/3'"
echo "$c"
bash -c "$c | jq"

sleep 5

echo
echo
echo "Credenciales inválidas"
c="curl -u admin:admin -s 'localhost:8080/users/3'"
echo "$c"
bash -c "$c | jq"

sleep 5

echo
echo
echo "Credenciales válidas"
c="curl -u admin:admin123 -s 'localhost:8080/users/3'"
echo "$c"
bash -c "$c | jq"
