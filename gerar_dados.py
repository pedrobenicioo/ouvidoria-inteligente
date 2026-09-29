# Autor: PEDRO HENRIQUE BENICIO DE OLIVEIRA | RGM: 33602697
"""Gera manifestacoes.json (40 manifestações sintéticas e anônimas) e duplicatas_reais.json (gabarito).
Uso: python gerar_dados.py"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))

# (id, data, categoria, texto)
DADOS = [
    ("M001", "2025-03-03", "infraestrutura", "O poste de iluminação da Rua das Flores está apagado há duas semanas e a rua fica completamente escura à noite, dificultando a passagem dos moradores."),
    ("M002", "2025-03-05", "saúde", "Fui à UPA com febre alta e esperei mais de cinco horas para ser atendido, sem nenhuma previsão de chamada nem informação da recepção."),
    ("M003", "2025-03-06", "infraestrutura", "Existe um buraco enorme na Av. Brasil, na altura do número 1200, que já causou dois acidentes com motos. Precisa de reparo urgente."),
    ("M004", "2025-03-08", "segurança", "Assaltos frequentes na parada de ônibus da Rua XV no período da noite. Precisamos de policiamento e câmeras de monitoramento no local."),
    ("M005", "2025-03-10", "educação",
     "Escrevo para relatar a situação da escola municipal do bairro Vila Nova. Desde o início do ano letivo, as turmas do quinto ano ficam sem professor titular em pelo menos dois dias por semana, e as crianças são apenas reunidas em um pátio sem nenhuma atividade. "
     "Além disso, o banheiro dos alunos está interditado há três meses, obrigando as crianças a esperarem em fila para usar o único banheiro dos funcionários. "
     "A merenda chega fria e em pouca quantidade, e várias vezes acaba antes de todos serem servidos. Por fim, o portão da escola vive aberto, sem porteiro, e pessoas estranhas já entraram durante o horário das aulas. Pedimos providências imediatas da Secretaria de Educação."),
    ("M006", "2025-03-11", "meio ambiente", "Lixo acumulado no terreno baldio ao lado da escola, com mau cheiro forte e presença de ratos e baratas. Solicito limpeza e fiscalização."),
    ("M007", "2025-03-12", "educação", "A escola municipal do bairro Jardim Esperança está sem merenda há uma semana e as crianças estão passando fome durante as aulas."),
    ("M008", "2025-03-14", "saúde", "O posto de saúde do meu bairro está sem médico há mais de um mês e ninguém consegue marcar consulta."),
    ("M009", "2025-03-15", "segurança", "Carros passam em alta velocidade na rua da creche. Faltam lombada e faixa de pedestres, e as crianças correm risco de atropelamento."),
    ("M010", "2025-03-17", "meio ambiente", "Esgoto a céu aberto na Rua das Acácias. O cheiro é insuportável e há risco de doenças para as famílias que moram ali."),
    ("M011", "2025-03-18", "infraestrutura", "A calçada em frente ao mercado municipal está quebrada e cheia de desníveis. Idosos e cadeirantes não conseguem passar com segurança."),
    ("M012", "2025-03-20", "educação", "Faltam professores de matemática na escola municipal do Centro. Os alunos do 8º ano estão sem essa matéria desde o começo do semestre."),
    ("M013", "2025-03-21", "meio ambiente", "Queimada em terreno vazio soltando muita fumaça o dia todo, prejudicando quem tem problemas respiratórios, principalmente crianças e idosos."),
    ("M014", "2025-03-24", "saúde",
     "Sou moradora do bairro São José e gostaria de registrar diversos problemas no atendimento de saúde da região. Minha mãe, idosa e diabética, precisou de consulta com endocrinologista e aguarda na fila do SUS há mais de oito meses, sem qualquer retorno da central de regulação. "
     "Quando ela passa mal, a ambulância demora mais de uma hora para chegar. Na farmácia do posto, faltam insulina e vários remédios de uso contínuo, e somos obrigados a comprar com o próprio dinheiro. "
     "Os agentes comunitários de saúde não visitam a rua há meses. Por último, o exame de sangue que ela fez foi perdido pelo laboratório e precisou ser repetido, atrasando ainda mais o tratamento."),
    ("M015", "2025-03-25", "segurança", "Ponto de tráfico de drogas funcionando abertamente na praça central, à vista de todos, sem nenhuma ação da guarda municipal."),
    ("M016", "2025-03-27", "educação", "O ônibus escolar da zona rural está quebrado e as crianças estão faltando às aulas por não terem como chegar à escola."),
    ("M017", "2025-03-28", "infraestrutura", "O asfalto da avenida principal está todo esburacado, os carros estão estragando pneus e suspensão."),
    ("M018", "2025-03-31", "meio ambiente", "Uma árvore caiu na calçada após a chuva forte e ninguém da prefeitura veio recolher os galhos, que bloqueiam a passagem de pedestres."),
    ("M019", "2025-04-02", "saúde", "A ambulância do SAMU demorou quase uma hora para chegar em uma emergência com meu pai, que estava com dor no peito."),
    ("M020", "2025-04-03", "infraestrutura",
     "Venho reclamar do abandono da Rua Sete de Setembro, no bairro Bela Vista. O asfalto está cheio de crateras que se enchem de água quando chove, e os moradores já perderam a conta de rodas e pneus danificados. "
     "As bocas de lobo estão entupidas de lixo e terra, e a cada temporal a rua vira um rio, com água entrando nas casas mais baixas. "
     "Três postes estão sem lâmpada, deixando o trecho da esquina até a praça totalmente às escuras, e por isso aumentaram os furtos. Também não há sinalização de trânsito: a placa de pare foi derrubada por um caminhão e nunca foi recolocada. Aguardamos uma vistoria da Secretaria de Obras."),
    ("M021", "2025-04-04", "segurança", "Não há câmeras de monitoramento na praça do bairro, onde furtos de celulares acontecem com frequência no fim da tarde."),
    ("M022", "2025-04-07", "saúde", "Falta atendimento no PSF da comunidade. Não tem doutor e os agentes de saúde não aparecem."),
    ("M023", "2025-04-08", "educação", "A creche municipal tem uma lista de espera enorme e várias mães não conseguem vaga para os filhos, o que as impede de trabalhar."),
    ("M024", "2025-04-09", "meio ambiente", "O rio que passa pelo bairro está poluído com óleo e lixo despejados, aparentemente, por uma indústria próxima. Há peixes mortos nas margens."),
    ("M025", "2025-04-11", "infraestrutura", "O bueiro entupido na esquina da Rua Sete causa alagamento toda vez que chove, e a água chega a invadir as lojas da região."),
    ("M026", "2025-04-14", "saúde", "Está faltando remédio para hipertensão na farmácia do posto de saúde, e tive que comprar com meu próprio dinheiro."),
    ("M027", "2025-04-15", "segurança",
     "Gostaria de relatar a insegurança que enfrentamos no bairro Santa Clara. Nos últimos meses, houve mais de dez assaltos a pedestres na avenida principal, sempre à noite, e a viatura da polícia só passa uma vez por turno. "
     "Existe também uma casa abandonada na esquina da Rua das Palmeiras, ocupada por usuários de drogas, que se tornou ponto de venda e esconderijo. "
     "Os postes da região vivem com lâmpadas queimadas, o que facilita a ação dos criminosos. Além disso, motoqueiros fazem manobras perigosas e correm em alta velocidade perto da escola, colocando em risco os estudantes. "
     "Pedimos reforço do policiamento, iluminação nova e demolição do imóvel abandonado."),
    ("M028", "2025-04-16", "educação", "A escola do bairro não tem acessibilidade: não há rampa de acesso, e alunos cadeirantes precisam ser carregados no colo para entrar."),
    ("M029", "2025-04-17", "meio ambiente", "Bar com som muito alto até de madrugada na Rua Nova. É impossível dormir e já liguei várias vezes para a fiscalização sem resposta."),
    ("M030", "2025-04-22", "infraestrutura", "O ponto de ônibus da Avenida Central não tem cobertura, e as pessoas se molham na chuva e sofrem com o sol forte."),
    ("M031", "2025-04-23", "infraestrutura", "A lâmpada queimada na praça deixa o local escuro à noite e afasta os moradores."),
    ("M032", "2025-04-24", "saúde", "Estou há meses esperando uma consulta com cardiologista pelo SUS, e a central de regulação não dá nenhuma previsão."),
    ("M033", "2025-04-28", "segurança", "Há uma casa abandonada na Rua Sete usada por usuários de drogas, e os moradores da vizinhança estão com medo de sair à noite."),
    ("M034", "2025-05-02", "educação", "A biblioteca da escola está fechada, sem funcionário responsável, e os livros estão mofando nas prateleiras."),
    ("M035", "2025-05-05", "educação", "Os alunos do oitavo ano estão sem aula de matemática há meses porque a escola não tem professor contratado para a disciplina."),
    ("M036", "2025-05-06", "meio ambiente", "A coleta de lixo não passa na minha rua há dez dias, e os sacos se acumulam na calçada atraindo animais."),
    ("M037", "2025-05-08", "saúde", "Faltou vacina contra a gripe no posto de saúde do centro, e vários idosos voltaram para casa sem serem vacinados."),
    ("M038", "2025-05-09", "meio ambiente",
     "Moro perto do córrego do bairro Alto da Serra e quero denunciar a degradação ambiental da região. Há meses um loteamento clandestino despeja entulho e esgoto direto no córrego, que já mudou de cor e exala mau cheiro. "
     "Todo o mato nas margens foi cortado e queimado, e a fumaça incomoda os vizinhos, muitos com asma e bronquite. "
     "Percebi também um aumento de mosquitos e ratos, e duas crianças da vizinhança tiveram dengue. Os pneus e o lixo jogados no terreno ao lado acumulam água parada. "
     "A coleta de lixo passa apenas uma vez por semana, insuficiente para o volume. Peço a fiscalização do órgão ambiental e a limpeza do córrego."),
    ("M039", "2025-05-12", "segurança", "O semáforo do cruzamento da Av. Central com a Rua 10 está desligado há dias, e o risco de acidentes é constante nos horários de pico."),
    ("M040", "2025-05-13", "meio ambiente", "Há muitos focos de mosquito da dengue em um terreno com pneus velhos e água parada. Peço fiscalização e limpeza urgente."),
]

# Pares de duplicatas semânticas (mesmo problema, palavras diferentes) — gabarito
DUPLICATAS = [["M003", "M017"], ["M008", "M022"], ["M012", "M035"]]


def main():
    registros = [{"id": i, "data": d, "categoria_oficial": c, "texto": t} for i, d, c, t in DADOS]
    assert len(registros) == 40 and len({r["id"] for r in registros}) == 40
    assert all(50 <= len(r["texto"]) <= 800 for r in registros), "tamanho fora de 50-800"
    longos = sorted(registros, key=lambda r: -len(r["texto"]))[:5]
    assert all(len(r["texto"]) > 500 for r in longos)
    with open(os.path.join(AQUI, "manifestacoes.json"), "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    with open(os.path.join(AQUI, "duplicatas_reais.json"), "w", encoding="utf-8") as f:
        json.dump(DUPLICATAS, f, ensure_ascii=False, indent=2)
    print("OK:", len(registros), "manifestações; longos:", [(r["id"], len(r["texto"])) for r in longos])


if __name__ == "__main__":
    main()

