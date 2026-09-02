#!/bin/sh

cd "$(dirname "$0")" || exit

echo "Una solicitud"
c="curl -s 'localhost:8080/movies/9/stats'"
echo "$c"
bash -c "$c | jq"

sleep 5

echo
echo
echo "Tiempo de 4 solicitudes en secuencia"
for i in $(seq 1 4); do
	echo "Intento $i:";
	c="curl -s 'localhost:8080/movies/8/stats'"
	time bash -c "$c >/dev/null"
done

sleep 5

echo
echo
echo "Prueba de la cola acotada"
uv run ./rendimiento_concurrente.py
