FROM mysql:8.0

# Копируем файл с настройками базы данных
COPY ./db/init.sql /docker-entrypoint-initdb.d/

# Настраиваем переменные окружения для подключения к базе данных
ENV MYSQL_ROOT_PASSWORD='DoLlitoS640M'
ENV MYSQL_USER='root'
ENV MYSQL_PASSWORD='DoLlitoS640M'
ENV MYSQL_DATABASE='hh_data'

CMD ["mysqld"]
