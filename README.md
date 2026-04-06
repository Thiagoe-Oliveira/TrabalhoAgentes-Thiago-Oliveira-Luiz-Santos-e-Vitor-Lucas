Documentação do Processo de Elaboração dos Agentes

Introdução

Este projeto apresenta a construção incremental de agentes inteligentes em um ambiente de grade bidimensional. A cada etapa, o agente evolui em complexidade, passando de um comportamento puramente reativo até um agente baseado em utilidade, capaz de tomar decisões otimizadas considerando custos e diferentes níveis de observabilidade.

O objetivo principal é demonstrar, de forma prática, os principais tipos de agentes estudados em Inteligência Artificial, bem como a aplicação dos conceitos de percepção, decisão e ação em ambientes controlados.

Etapa 1 – Agente Reativo Simples (Sem Memória)
Descrição

Na primeira etapa, foi desenvolvido um agente reativo simples que se movimenta em um ambiente em forma de grade. O agente não possui memória e toma decisões apenas com base na percepção atual.

Seu objetivo é alcançar as quatro fronteiras do ambiente: topo, base, esquerda e direita.

Funcionamento

O agente:

* percebe apenas sua posição atual
* identifica quais movimentos são possíveis (sem sair da grade)
* escolhe aleatoriamente um movimento válido

Não há armazenamento de estados anteriores, nem estratégia de otimização.

PEAS

* Performance: alcançar todas as fronteiras do ambiente
* Environment: grade bidimensional finita, sem obstáculos
* Actuators: movimentos (cima, baixo, esquerda, direita)
* Sensors: percepção local da posição e limites da grade

Espaço de Estados

* Estados: posição do agente na grade
* Estado inicial: posição aleatória
* Ações: movimentos válidos
* Objetivo: visitar ao menos uma vez cada fronteira
* Transições: determinísticas (movimento altera posição)

Etapa 2 – Agente Reativo Baseado em Modelo

Descrição

Nesta etapa, o agente passa a possuir memória interna, permitindo registrar quais posições já foram visitadas. Além disso, o ambiente pode conter obstáculos.

O objetivo do agente é maximizar a cobertura do ambiente acessível, minimizando revisitas desnecessárias.

Funcionamento

O agente:

* mantém um modelo interno com células visitadas e contagem de visitas
* prioriza movimentos para posições ainda não visitadas
* caso todas as opções já tenham sido visitadas, escolhe a menos visitada

Também é calculado o conjunto de células alcançáveis a partir da posição inicial, garantindo uma meta realista.

PEAS

* Performance: maximizar a cobertura do ambiente acessível
* Environment: grade bidimensional com obstáculos
* Actuators: movimentos nas quatro direções
* Sensors: percepção local e detecção de obstáculos adjacentes

Espaço de Estados

* Estados: posição atual + histórico de visitas
* Estado inicial: posição aleatória em célula livre
* Ações: movimentos válidos que não colidem com obstáculos
* Objetivo: visitar todas as células alcançáveis
* Transições: determinísticas

Etapa 3 – Agente Baseado em Objetivo

Descrição

Nesta etapa, o agente passa a ter um objetivo explícito: sair de uma posição inicial e alcançar uma posição final.

Para isso, é utilizado um algoritmo de busca em largura (BFS) para encontrar um caminho válido no ambiente com obstáculos.

Funcionamento

O agente:

* recebe um ponto inicial e um destino
* calcula previamente um caminho utilizando busca em largura
* executa o caminho passo a passo

Caso não exista caminho válido, um novo cenário é gerado.

PEAS

* Performance: alcançar o destino a partir da origem
* Environment: grade com obstáculos
* Actuators: movimentos nas quatro direções
* Sensors: conhecimento completo do ambiente

Espaço de Estados

* Estados: posições possíveis na grade
* Estado inicial: posição inicial definida
* Estado objetivo: posição final
* Ações: movimentos válidos
* Transições: determinísticas
* Estratégia: busca em largura (BFS)

Etapa 4 – Agente Baseado em Utilidade

Descrição

Na etapa final, o agente passa a considerar custos associados às células do ambiente, buscando minimizar o custo total do trajeto até o destino.

São implementados dois cenários:

* ambiente completamente observável
* ambiente parcialmente observável

Funcionamento

O agente utiliza o algoritmo de Dijkstra para encontrar o caminho de menor custo.

No modo:

* completamente observável: todos os custos são conhecidos desde o início
* parcialmente observável: os custos são revelados gradualmente conforme o agente explora o ambiente

PEAS

* Performance: minimizar o custo total do caminho até o destino
* Environment: grade com custos variáveis por célula
* Actuators: movimentos nas quatro direções
* Sensors: percepção total ou parcial dos custos

Espaço de Estados

* Estados: posição do agente e conhecimento do ambiente
* Estado inicial: posição inicial
* Estado objetivo: posição final
* Ações: movimentos válidos
* Transições: determinísticas com custo associado
* Função de custo: soma dos custos das células percorridas
* Estratégia: algoritmo de Dijkstra
