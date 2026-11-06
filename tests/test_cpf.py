import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cpf import normalizar_cpf, cpf_valido


class TestNormalizarCPF(unittest.TestCase):
    def test_remove_pontuacao(self):
        self.assertEqual(normalizar_cpf("529.982.247-25"), "52998224725")

    def test_remove_espacos(self):
        self.assertEqual(normalizar_cpf(" 529 982 247 25 "), "52998224725")

    def test_none(self):
        self.assertEqual(normalizar_cpf(None), "")

    def test_ja_numerico(self):
        self.assertEqual(normalizar_cpf("52998224725"), "52998224725")


class TestCpfValido(unittest.TestCase):
    def test_cpf_valido_conhecido(self):
        self.assertTrue(cpf_valido("529.982.247-25"))
        self.assertTrue(cpf_valido("52998224725"))

    def test_cpf_valido_mascarado(self):
        self.assertTrue(cpf_valido("123.456.789-09"))  # may be invalid; replaced below

    def test_rejeita_tamanho_errado(self):
        self.assertFalse(cpf_valido("1234567890"))
        self.assertFalse(cpf_valido("123456789012"))

    def test_rejeita_todos_iguais(self):
        for d in "0123456789":
            self.assertFalse(cpf_valido(d * 11))

    def test_rejeita_digito_verificador_errado(self):
        self.assertFalse(cpf_valido("52998224724"))  # last digit wrong
        self.assertFalse(cpf_valido("52998224735"))  # second-to-last wrong

    def test_rejeita_nao_numerico(self):
        self.assertFalse(cpf_valido("abcdefghijk"))
        self.assertFalse(cpf_valido(""))

    def test_cpf_valido_gerado(self):
        # generate a valid CPF and ensure accepted
        def calc(cpf):
            cpf = list(cpf)
            for pos in (9, 10):
                s = sum(int(cpf[i]) * (pos + 1 - i) for i in range(pos))
                d = (s * 10) % 11
                d = 0 if d in (10, 11) else d
                cpf.append(str(d))
            return "".join(cpf)

        base = "390533447"
        valido = calc(base)
        self.assertTrue(cpf_valido(valido))
        self.assertEqual(len(valido), 11)


if __name__ == "__main__":
    unittest.main()
