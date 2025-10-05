def validar_cnpj(cnpj: str) -> bool:
    cnpj = ''.join(filter(str.isdigit, cnpj))

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6] + pesos_1

    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(d) * p for d, p in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    dv1 = calcular_digito(cnpj[:12], pesos_1)
    dv2 = calcular_digito(cnpj[:12] + dv1, pesos_2)

    return cnpj[-2:] == dv1 + dv2
