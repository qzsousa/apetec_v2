import re


def normalizar_cpf(cpf) -> str:
    if cpf is None:
        return ""
    return re.sub(r"\D", "", str(cpf))


def cpf_valido(cpf) -> bool:
    cpf = normalizar_cpf(cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    for t in (9, 10):
        soma = sum(int(cpf[i]) * (t + 1 - i) for i in range(t))
        digito = (soma * 10) % 11
        if digito in (10, 11):
            digito = 0
        if digito != int(cpf[t]):
            return False
    return True
