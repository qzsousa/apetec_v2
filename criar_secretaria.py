import sqlite3
from passlib.hash import bcrypt

conexao = sqlite3.connect("database.db")

cursor = conexao.cursor()

sql = "INSERT INTO secretaria (cpf, nome, telefone, email, senha) VALUES (?, ?, ?, ?, ?)"
dados = ("47266774896", "Pablo Nascimento Vieira de Sousa", "11952437282", "nascpablo1709@gmail.com", bcrypt.hash("thuane2405"))

cursor.execute(sql, dados)

conexao.commit()

cursor.close()
conexao.close()