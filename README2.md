# SoftwareDesignFinal_AusserlechnerM_WalserN

## Überblick
Dieses Programm ist im Rahmen des Abschlussprojekts der Lehrveranstaltung „Softwaredesign“ entstanden.

Die Anwendung ermöglicht die Modellierung von Strukturen aus Massepunkten und Federn in verschiedenen Formen. Konkret können rechteckige Balken mit variablen Abmessungen generiert, eigene Zeichnungen direkt in der Benutzeroberfläche erstellt oder Bilder (bis zu einer Größe von 120x120 Pixeln) importiert werden. Diese Modelle lassen sich anschließend mit Lagerbedingungen sowie äußeren und inneren Kräften beaufschlagen.

Für die gewählten Randbedingungen kann eine Verformungssimulation als auch eine Topologieoptimierung durchgeführt werden. Hierfür stehen verschiedene konfigurierbare Algorithmen zur Verfügung.

Zudem bietet das Programm die Möglichkeit, Projekte zu speichern und zu laden. Die Berechnungsverläufe können als GIF und die finalen Ergebnisse als PNG-Datei exportiert werden.

## Installation und Ausführung
### 1. Repository clonen
```bash
git clone https://github.com/Froggy875/SoftwareDesignFinal_AusserlechnerM_WalserN.git
cd SoftwareDesignFinal_AusserlechnerM_WalserN/
```
### 2. Virtuelle Umgebung erstellen und aktivieren (Empfohlen)
Es ist wird empfohlen, eine virtuelle Umgebung (`venv`) zu nutzen, um Konflikte mit anderen Python-Projekten auf deinem System zu vermeiden.

**Unter Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Unter macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

*(Wenn die Aktivierung erfolgreich war, ist `(.venv)` vorne in der Kommandozeile sichtbar).*

### 3. Abhängigkeiten installieren
Sobald die virtuelle Umgebung aktiv ist, benötigten Bibliotheken installieren:
```bash
pip install -r requirements.txt
```

### 4. App starten
Mit aktivierter Umgebung und installierten Abhängigkeiten kann die Anwendung nun gestartet werden:

```bash
streamlit run .\src\main.py
```

*(Die Web-App öffnet sich danach automatisch in deinem Standard-Browser).*

## UML-Diagramm 
[![](https://mermaid.ink/img/pako:eNq1WOtOIzcUfhVrtCslJaQESggRWqmwqy7dbqka-qeKZHlmPJOzeOyR7VDClrfpm_TFeuyZSTyToaBK5UcwPhefy3cu4WuUqJRH8ygRzJj3wHLNiqUk-PP2LblSmpMPghdcWlPdej7yMwqRr9WN-zkAaQmkwYUsx0xrtiGlMn3XmdIJDwgCjCUZPPBeJSmYUrDEG1LRn5YyNGhRapB5y6RMKGZJyqUBu9m7L7lkouf-LrjJuaUpaJ5YUHIwJHZditDmT1SohAmkFMxqeGiRcqHifppTa6xmICmXXOcbZPKPdzzDBCysXid2jVn4zCTLA_9rt7f0wPNDikksV0Q-jH9wh-BplqZUYu4G7oNCOiL-oOIvww6X8QFt-CjUnHj8MiIVsSvm_AqVDz1Muo4_r3dYZzGQ0LxQ97yttedFgxF0AOqQeJo_R_IRQlI3QHJdxFxTlW31grS99EZ5m24VIiaxeO9-hTE1hhex4NRsjOVFD5qMEvcc7z3i-0HeZPtyDSLlOkz6xYWxzELy7l0IhERJifClkkO-ipU2A9PoqANfsHL4JrAi0ZxZTh3omcwFhp2WCn009A-UaM6r4ZudNfvSmVYFajZ3A_dBj1PqndoXCrF-U1oo4JHrVqe5ZIbfqlIJlW-2HK0639WA6bHINyYJFpioUooxWbdSRn3gd3mJlRIhWfM66TUiQlrsEoEZx9jLBP0GYbkeACrCZ5ROQWI4zIhoWoAMMdHJ7IfFDXWe9ntIsckka-Ei63PmuwZ49HVQRsFQXzMsFkEddl1KVjy5a8AB99gfK15Eb1VxPSJbEyr9oopjWAA9Pn1kOv0EQtB-xwy3pHqwakumk7hkrTH6lmJANXNNOKCrWuPAMu0qGpGGvjuuEbbch52MGZLcRYxZpZ81dKEy-4KhBlnoHfL0GOvSUNWTq8L_5sd4PN6ztKridZm6wNdd11jIMsmxn5hBxhLkHYbMpeYl01ssVsgLGVhZik09eRquFqz-BaeL68-_PBOil_ysxmvDsT9-fQiVqyY_saEVxFcE6ZV-m0q7w3zDurvqON-K_tYsqpK2yIjUEKzRh2O9Xpla7-8qKFlha-V7U9_92nbD3ywIr518S94zy2LsDmEmmrurqohVZxgswDVvq2R7HoCsOtW-eDgDsI-SktlwLt6C3Ly_JGncmaPWNxr_SSUrsHH4cz94uMYu3AXOxYVF3WmMmanIHjiN2R0VaDbvV3NgNyUnN5c_0qufvl8sAgKXbsUduGXFTYgQctxTXM5Rb--Dt1D8Lw8inHlP4qtHrwtc9T48lErbl4f8QQa5a9wliAEeccZ68e6-AxmNN9a1DFzwHWbTdVWiKOAJHQFwShoRrzbges7m6-KVNtd7gl8RQJZr3LMRkFhIK83NCrsA2sf0nRtnuD77-KMFfZsRlsqvXFSNfgVlbWD9dWAZTZYRUYeHeDrGk__aMif3XMcgU16X3m6B-AY5ax4s39Xff4lellr7s0zNejYevwsk56SqvkcArm0Ywf4dx5kdShcqhQwed8L9Yhd_otzePvGiRLuzh9bt7ybbJ_bH-4si-4O2yWRQZp67Xev9PJ3yrJj2W6NLRKd1zHHxyHFv07t49st1nmjJRaMo15BGc0wTH0UF1wVzf0Ye_8vIrnAOLKM5Hh2cl9FSPqFMyeTvShWNmFbrfBXNMyYM_lWNm_qb-JaFI1z1ldu4ovns6NzriOZfo4doPpmcjU_OzyZnRyfTo-Oj6WQ2ijbR_HhyOp6dnU9ms-nk9PRkejZ7GkWP_tmj8Ww6O5kdTSbTs_PvTo-nKMFTQI8_1_8McL-e_gHz1iz4?type=png)](https://mermaid.live/edit#pako:eNq1WOtOIzcUfhVrtCslJaQESggRWqmwqy7dbqka-qeKZHlmPJOzeOyR7VDClrfpm_TFeuyZSTyToaBK5UcwPhefy3cu4WuUqJRH8ygRzJj3wHLNiqUk-PP2LblSmpMPghdcWlPdej7yMwqRr9WN-zkAaQmkwYUsx0xrtiGlMn3XmdIJDwgCjCUZPPBeJSmYUrDEG1LRn5YyNGhRapB5y6RMKGZJyqUBu9m7L7lkouf-LrjJuaUpaJ5YUHIwJHZditDmT1SohAmkFMxqeGiRcqHifppTa6xmICmXXOcbZPKPdzzDBCysXid2jVn4zCTLA_9rt7f0wPNDikksV0Q-jH9wh-BplqZUYu4G7oNCOiL-oOIvww6X8QFt-CjUnHj8MiIVsSvm_AqVDz1Muo4_r3dYZzGQ0LxQ97yttedFgxF0AOqQeJo_R_IRQlI3QHJdxFxTlW31grS99EZ5m24VIiaxeO9-hTE1hhex4NRsjOVFD5qMEvcc7z3i-0HeZPtyDSLlOkz6xYWxzELy7l0IhERJifClkkO-ipU2A9PoqANfsHL4JrAi0ZxZTh3omcwFhp2WCn009A-UaM6r4ZudNfvSmVYFajZ3A_dBj1PqndoXCrF-U1oo4JHrVqe5ZIbfqlIJlW-2HK0639WA6bHINyYJFpioUooxWbdSRn3gd3mJlRIhWfM66TUiQlrsEoEZx9jLBP0GYbkeACrCZ5ROQWI4zIhoWoAMMdHJ7IfFDXWe9ntIsckka-Ei63PmuwZ49HVQRsFQXzMsFkEddl1KVjy5a8AB99gfK15Eb1VxPSJbEyr9oopjWAA9Pn1kOv0EQtB-xwy3pHqwakumk7hkrTH6lmJANXNNOKCrWuPAMu0qGpGGvjuuEbbch52MGZLcRYxZpZ81dKEy-4KhBlnoHfL0GOvSUNWTq8L_5sd4PN6ztKridZm6wNdd11jIMsmxn5hBxhLkHYbMpeYl01ssVsgLGVhZik09eRquFqz-BaeL68-_PBOil_ysxmvDsT9-fQiVqyY_saEVxFcE6ZV-m0q7w3zDurvqON-K_tYsqpK2yIjUEKzRh2O9Xpla7-8qKFlha-V7U9_92nbD3ywIr518S94zy2LsDmEmmrurqohVZxgswDVvq2R7HoCsOtW-eDgDsI-SktlwLt6C3Ly_JGncmaPWNxr_SSUrsHH4cz94uMYu3AXOxYVF3WmMmanIHjiN2R0VaDbvV3NgNyUnN5c_0qufvl8sAgKXbsUduGXFTYgQctxTXM5Rb--Dt1D8Lw8inHlP4qtHrwtc9T48lErbl4f8QQa5a9wliAEeccZ68e6-AxmNN9a1DFzwHWbTdVWiKOAJHQFwShoRrzbges7m6-KVNtd7gl8RQJZr3LMRkFhIK83NCrsA2sf0nRtnuD77-KMFfZsRlsqvXFSNfgVlbWD9dWAZTZYRUYeHeDrGk__aMif3XMcgU16X3m6B-AY5ax4s39Xff4lellr7s0zNejYevwsk56SqvkcArm0Ywf4dx5kdShcqhQwed8L9Yhd_otzePvGiRLuzh9bt7ybbJ_bH-4si-4O2yWRQZp67Xev9PJ3yrJj2W6NLRKd1zHHxyHFv07t49st1nmjJRaMo15BGc0wTH0UF1wVzf0Ye_8vIrnAOLKM5Hh2cl9FSPqFMyeTvShWNmFbrfBXNMyYM_lWNm_qb-JaFI1z1ldu4ovns6NzriOZfo4doPpmcjU_OzyZnRyfTo-Oj6WQ2ijbR_HhyOp6dnU9ms-nk9PRkejZ7GkWP_tmj8Ww6O5kdTSbTs_PvTo-nKMFTQI8_1_8McL-e_gHz1iz4)

## Komponentendiagramm
[![](https://mermaid.ink/img/pako:eNqVVmtv4jgU_StWRjOakaC8Ic2uRipQKiQo1TKdDzOskEkMeBvsyI-20PS_77WdBNIy2h2kFts59_j6-N4TXryQR8QLvHXMn8ItFgp9Gy4Ygs_Hj2iu9jFlGzcPYyzlkKyRVABjEIbWNI6DD1GruW6uK1IJ_kCCD6teI2yE2bT6RCO1DZrJcyXkMRfB05Yq8scbRk0zqvbgatSpF1Qt379uDX6LKqEJgZzz3JqNy-6oVRA2LnvdYfO3CEMucrLR6NKvH7MbdXqDYvr_yKJVRnU5aPb6R6pevzG6-r28tKKxzNi69d7Q7xds7U7nqtv-L7bilq-SBF0zJfbojlOm3PoUUzaiMfm58HYwvEj26PMb4JeF93cQBEU55JRSrzYCJ1s0EpwpwiIEJMW4hu7HaIL3RKDPcyUI3sXUUrlg87kfQ0DIdwlnhCkJe_-5El_N9tW5IpoIzTboE_pOyZPMktD0GP6dSoh_pFLjmB6IyOOnWCUxVzFdoTv4fhsKyb07wV1eTUBYjLPkB3AgweOYiHL2AxyHBmvOAEMdY0U5W-aFmWczwRFh5hRcrIggcCcsSyhHHin7msbRnMePhnRlJkvMoqU0K0u4Zh0qLQrmK71eYQ3Uo-vpLylniZpwngAfTxTdgU7viWb2iZVbVufhNiZ0Tc4yntNuYBoH-O13ptmQm2JCE76hYVk1e0QiAF-kkS1BNm5L04nHgLmFneJNjX5CJCa7rGrOhhnN7DZ2kB_1Bs4Wbs1B5V4qYPhyLniWSSVOZCso5uPpXQVdz2fvQs-pM54Zbca1GaR8D61MFSWypMh4txkzwNAd3pAlhW4Q6kQN2_8l9EyrAk6efw0_l84QK7zC0l5YMbaXVspp2P-LJBww0WopYCSp4mKfKeA2ilancGgS5uAhjEgIcHdNkghatOf7yG-U7Yf9n58hNMvm4h_JmRXaPUNTojA8tG3z5W387d0PE7zDSsAebGmBNRt-wZID2Jt8gIW5gnX5luBEILDHarWK-uRAiSkPaFkNJjY0dOtYS2kelx0TVr6mc2OKRKHC4cDUUvhzUHDAU1Af-j_cMkufFv7xBmp8D_iyLkzzBi6hrsWB6I0yDmi8T7reTc28hJtgEinYiD1iWbsHU8SRTF3BlXdNTFeYfW_Go9rd7U2a1VkuT56rYzUmppw26MlMRHpiXS7iOLcxfayBnCrA1uydpLkTnIVPOJEggm3RNOtlB8zksKiRJlvIGWuZHlvWwU5YwY8MeMzgBcYOFLRSaeYqDuXoXZruhsjJ3ifAYg-L_U4EhgqytwWgB7CmI7wsbyburVYQXB2zRCtI2TXZOYHtteWkVSt0GX6qQs5ednE4a1SOcf_dig28gbfRWqGDBgXXadbEOcqMXTLgV6oG9QjoFSjnuvId2bGEplkvpqY5vYq3ETTyAjgMqXg7IuDFAFPvxTAsPLUFD154ATIGIB4W3oK9QkyC2Q_Od3mY4Hqz9YI1jiXMdGK6fEgxWNoRYq9iwDVTXtCpdy2HF7x4z15Qbfuti0ar1Wq2636n3ulVvL0XNPz2Ravb9tsNv3XZarf9zmvFO9hdGxe9VrdX7_iX3Z7vN5udZsUjkfHAqfsVbX9Mv_4L3Wy7aQ?type=png)](https://mermaid.live/edit#pako:eNqVVmtv4jgU_StWRjOakaC8Ic2uRipQKiQo1TKdDzOskEkMeBvsyI-20PS_77WdBNIy2h2kFts59_j6-N4TXryQR8QLvHXMn8ItFgp9Gy4Ygs_Hj2iu9jFlGzcPYyzlkKyRVABjEIbWNI6DD1GruW6uK1IJ_kCCD6teI2yE2bT6RCO1DZrJcyXkMRfB05Yq8scbRk0zqvbgatSpF1Qt379uDX6LKqEJgZzz3JqNy-6oVRA2LnvdYfO3CEMucrLR6NKvH7MbdXqDYvr_yKJVRnU5aPb6R6pevzG6-r28tKKxzNi69d7Q7xds7U7nqtv-L7bilq-SBF0zJfbojlOm3PoUUzaiMfm58HYwvEj26PMb4JeF93cQBEU55JRSrzYCJ1s0EpwpwiIEJMW4hu7HaIL3RKDPcyUI3sXUUrlg87kfQ0DIdwlnhCkJe_-5El_N9tW5IpoIzTboE_pOyZPMktD0GP6dSoh_pFLjmB6IyOOnWCUxVzFdoTv4fhsKyb07wV1eTUBYjLPkB3AgweOYiHL2AxyHBmvOAEMdY0U5W-aFmWczwRFh5hRcrIggcCcsSyhHHin7msbRnMePhnRlJkvMoqU0K0u4Zh0qLQrmK71eYQ3Uo-vpLylniZpwngAfTxTdgU7viWb2iZVbVufhNiZ0Tc4yntNuYBoH-O13ptmQm2JCE76hYVk1e0QiAF-kkS1BNm5L04nHgLmFneJNjX5CJCa7rGrOhhnN7DZ2kB_1Bs4Wbs1B5V4qYPhyLniWSSVOZCso5uPpXQVdz2fvQs-pM54Zbca1GaR8D61MFSWypMh4txkzwNAd3pAlhW4Q6kQN2_8l9EyrAk6efw0_l84QK7zC0l5YMbaXVspp2P-LJBww0WopYCSp4mKfKeA2ilancGgS5uAhjEgIcHdNkghatOf7yG-U7Yf9n58hNMvm4h_JmRXaPUNTojA8tG3z5W387d0PE7zDSsAebGmBNRt-wZID2Jt8gIW5gnX5luBEILDHarWK-uRAiSkPaFkNJjY0dOtYS2kelx0TVr6mc2OKRKHC4cDUUvhzUHDAU1Af-j_cMkufFv7xBmp8D_iyLkzzBi6hrsWB6I0yDmi8T7reTc28hJtgEinYiD1iWbsHU8SRTF3BlXdNTFeYfW_Go9rd7U2a1VkuT56rYzUmppw26MlMRHpiXS7iOLcxfayBnCrA1uydpLkTnIVPOJEggm3RNOtlB8zksKiRJlvIGWuZHlvWwU5YwY8MeMzgBcYOFLRSaeYqDuXoXZruhsjJ3ifAYg-L_U4EhgqytwWgB7CmI7wsbyburVYQXB2zRCtI2TXZOYHtteWkVSt0GX6qQs5ednE4a1SOcf_dig28gbfRWqGDBgXXadbEOcqMXTLgV6oG9QjoFSjnuvId2bGEplkvpqY5vYq3ETTyAjgMqXg7IuDFAFPvxTAsPLUFD154ATIGIB4W3oK9QkyC2Q_Od3mY4Hqz9YI1jiXMdGK6fEgxWNoRYq9iwDVTXtCpdy2HF7x4z15Qbfuti0ar1Wq2636n3ulVvL0XNPz2Ravb9tsNv3XZarf9zmvFO9hdGxe9VrdX7_iX3Z7vN5udZsUjkfHAqfsVbX9Mv_4L3Wy7aQ)


# TopologieOptimierung
Zur Topologieoptimierung wurden drei Algorithmen ESO_HardKill_Optimizer, ESO_SoftKill_Optimizer und SIMP_Optimizer implementiert. Sie erben alle von der Hauptelternklasse BaseTopologyOptimizer, wobei die beiden ESO Optimizer dies indirekt über eine Subelternklasse ESO_BaseOptimizer tun.

## ESO_HardKill_Optimizer: Evolutionary Structural Optimization Hard Kill Optimizer
![UML Diagram](https://www.plantuml.com/plantuml/png/LPB1JkD038RlaV8EFY50j89hLY0uK408iHAhHU8sRPp4wcGciZs0zcLu2qxS-cBhILDGRpCUV_R__vfBKSUQUbyMuwaioY94HM1gExi1_8b3zB4bZ8DIJyWfjBd-sx7hKP4hU8WrUdy23qu40sETraenIEFM6ZatNuKcSZsoktOGwfEtUKl7MtHkv7pBmB-tEPp20Pnb-YK9hRg9VfnacCPlQRdfbdmZBMy-DnyOAdXIf8RQDIf9xvJf_GHks0qT1b4sWSc4OQWXkyskgqaM1L9odiHsOFYLdnW7T6COrJqSGu9pM41mgywEVlCfOvizFfjApJj9mSnEUGmfh4siIm9_aIs7tdnO7TcKmzAshBgm6_6I08Cso5QfSNz2i_bYg0a5uSvoTpbZuyNow7Vy7l0zoO8Cc0mJdOqTqzgHshg3juuymk5FomKyHU-tboCWWSDdr_5HMSmkOE6yhBendEgQMrm6oiWhITgFJZGEPN5fPiO_zXy0)

### Funktionsweise
Dieser Algorithmus wurde als Grundanforderung nach dem UML-Diagramm von Julian Huber & Matthias implementiert. Er nutzt das „Hard-Kill“-Verfahren, um den Materialanteil einer Struktur iterativ auf ein Zielverhältnis zu reduzieren, indem ineffiziente Knotenpunkte vollständig gelöscht werden.

In jedem Iterationsschritt wird das globale Gleichungssystem $K \cdot u = F$ gelöst und die Verformungsenergie der Knoten berechnet. Die Knoten mit der geringsten Energie werden anschließend entfernt. Zwei Sicherheitsmechanismen garantieren dabei physikalisch tragfähige Ergebnisse: Lager- und Lasteinleitungsknoten sind vor der Löschung geschützt, und eine fortlaufende Prüfung der Verbindungen stellt den strukturellen Zusammenhalt sicher. Dieser Prozess wiederholt sich mit adaptiv ansteigender Entfernungsrate, bis der gewünschte finale Materialanteil erreicht ist.

# Beispiel Messerschmitt mit Bölkow–Blohm Balken


## ESO_Softkill_Optimizer: Evolutionary Structural Optimization SoftKill Optimizer
![UML Diagram](https://www.plantuml.com/plantuml/png/NLB1ZjD03BrNoZ_uX5gKLgp4gOZLhWG5LAr05B7INj2qSHAh4q_acMaHFyEbtx0dRlcnzIGfIxdDoC_FxptxnWSZ8JOscsIJ_frDs0K4eQhMDy0trphhAaBN1ce89N85quqhmtnDriuIveiHqs10MSATAz3Q7EwCzyY2HTm7SknBimzESbYHLPoOWgA7gVneY7kAMowT53txcGGyDT7gnAsHWN2XV8k12NuT5_0ANi1L3diaHjWGLz4QeT2T0d8YVOYUTlL8-ddK7p272YkhgA2QdmscZezaIrz9zzZzHbx29Y2LLEc0u1iJX7xcy45CMoFx86ejgZBfJXfWFsYqbqsG2qWvfbYNenrY2cGiUHM1_4OBN_zsyjW91oTRBPCwECUZIC4MJR-EvHfUGeIti08skrgVjdlqFPqMxvKh37f1mnosq4RUgq-ZWNz7qPWRpKDRKDGqf6cxciyCwwIQno93eqIZiZ6n4VSGmU_gOtTAuWkyc5HsVmGAGe_mIJjDEW2TupN_vjn_eMpxJ0NJTya3giChdB-UwOOPesBqZ0xAvyEyRxtGFSG3nveimlJsV-WrR9ormsS6f7TtRshHivjVhupLsMaNxwN2BLF27yZ7V_VaWskpoOtwr6qz0G00)

### Funktionsweise

Dieser Algorithmus ist eine Weiterentwicklung des **ESO-Hard-Kill-Optimizers** und zielt darauf ab, dessen numerische Schwächen zu beheben sowie durch einen räumlichen Filter natürlichere Strukturen zu erzeugen.
Anstatt ineffiziente Knotenpunkte vollständig zu löschen, werden die Verbindungen derer iterativ Abgeschwächt: Das Material wird über einen sehr geringen Dichtefaktor (z.B. $10^{-4}$) lediglich künstlich „weich" gemacht.
Da die Dimension der Steifigkeitsmatrix $K$ dabei konstant bleibt, werden Singularitäten beim Lösen des Gleichungssystems $K \cdot u = F$ und daraus resultierende Solver-Abstürze effektiv verhindert. Der Nachteil davon ist, dass die Matrixgröße mit steigender Interationszahl nicht sinkt, damit und durch die Filtervorbereitung ergibt sich eine etwas längere Berechnungszeit.

# Beispiel Messerschmitt mit Bölkow–Blohm Balken



## SIMP_Optimizer: Solid Isotropic Material with Penalization
![UML Diagram](https://www.plantuml.com/plantuml/png/VLJBRjim4BmRy3_iAP0AEKskJfCcJMgqIFD07RH0KC2WhRMqCBaKICfv_4ml-GQVUjEFTIahZjr3Bu9iScPdPyO-zK6vK1lTx_a5SQMSCf3ZNDKwtE5ZEDDKi44EC9C7kdvFBaP8lySs83WgIda7kBELrROWj5KWG-XgBY0PVxswJUFnRIH68HZ2bSrHwmpk2VNIwbhO8H7A0iF4AEydJWMoQGP6FKugPAN3KmOZqe9sAgVQG-8cXhWbFkEvTNaxxfKQF9bQYuIfShjZdX_suG3su3231H8ZZ8cBMYj7eNa9o97mllOqApl2cswPW8Am78Xh-QJZ1RYGPy1bF2JTRYkQo2YDSArcfLWnfKB6X5Rd5z9pNxXcrVn67i9OGFFriJSgE7hCm3Kl4aGxl5itWp6ofq3BJc06trJX51Suk9A4gDAqKC5ABCWvn4HYGCFE1v4JI6doeZcQF8x1vQriXkCTPpo6P-Jqg8L_tmZXJWWihPiA2KLavtvxrs65gYt0y7OTrM2a5g88Aa1NDgl8aKp9RwUPIWGNdGmb8r3oOsZ-o8G2fyX7aQ_bl8HtK8lK4R1OAg-wMVdj2__u0ydPL8lA64T-_ZvtfKr1IMD-e9EU6FbUu3A64E8-ivB_nsOeRALYNiqej1o7RU0rrhXPIL01jOURyq4SgyhM_4_aSI75vbGcUwcLsIROsB48zLjYUz6rTQNM5veNphkVrdaPQv3khF6Q1poK99Zaql8oUihFm14laKY6ylBn5tS4S78C1_i7Xo2LYQ5zs0ag1Kak-IahI8a79p1Isi_ATKi-nx2Ol4TOadzJVRJ-Zx1LltSghHJp_W80)


## Disclaimer

Dieser Algorithmus ist mit Abstand der komplexeste und liefert auch die plausibelsten Ergebnisse. Es sei erwähnt, dass bei der Entwicklung dieses Algorithmus stark auf Künstliche Intelligenz gesetzt wurde. Trotzdem haben sich beide Entwickler (Mathias Außerlechner und Nils Walser) intensiv mit dem mathematischen Hintergrund, mit Stift und Papier als auch mit der Implementierung in Python, auseinandergesetzt. Es wurden trotz KI-Einsatz viele Stunden in die Verbesserung und Auseinandersetzung investiert. Es sei auch Joachim Spitaler erwähnt, mit dem sich viele Stunden über die SIMP-Methode ausgetauscht wurde.

## Funktionsweise
Das Ziel ist, eine Materialverteilung zu finden die bei gegebenen Lasten die Steifigkeit maximiert, unter der Nebenbedingung eines festen Materialbudgets. Jedem Element $e$ wird eine kontinuierliche Dichte $\rho_e$ als Variable zugewiesen. Formal:

$$ \text{minimiere:} \qquad C = F^T \cdot u \qquad \text{über $\rho$, unter den Bedingungen:} \quad K(\rho) \cdot u = F, \quad \sum_e \rho_e \cdot v_e \leq V_{Ziel}$$

wobei $C$ die Compliance (globale Nachgiebigkeit), $F$ der Kraftvektor, $u$ der Verschiebungsvektor, $K$ die Steifigkeitsmatrix und $V_{target}$ das Zielvolumen ist. Die Volumenbeschränkung koppelt alle Variablen, das Problem lässt sich nicht elementweise lösen, sondern erfordert ein globales Optimierungskriterium.

Da eine kontinuierliche Dichte physikalisch unsinnige Zwischenwerte erzeugt, werden diese durch das Potenzgesetz $E_e(\rho_e) = \rho_e^p \cdot E_0$ abgeschwächt, wobei $E_0$ der Elastizitätsmodul des Vollmaterials und $p$ der schrittweise erhöhte Penalty-Faktor ist. Zwischendichten werden dadurch strukturell unattraktiv und der Algorithmus treibt $\rho_e$ implizit gegen $\rho_{min}$ oder $1$.

Nach jedem Lösen von $K \cdot u = F$ wird berechnet, wie wertvoll Material an jeder Stelle ist, das wird anhand der Ableitung der Compliance nach der Elementdichte beurteilt:

$$\frac{\partial C}{\partial \rho_e} = -p \cdot \rho_e^{p-1} \cdot u_e^T \cdot K_e^0 \cdot u_e$$

wobei $u_e$ der lokale Verschiebungsvektor und $K_e^0$ die Elementsteifigkeitsmatrix bei Volldichte ist. Um numerische Artefakte zu vermeiden, werden diese Sensitivitäten über einen Radius $r_{min}$ räumlich gefiltert.

Da die Volumenbeschränkung direkt in die Optimierung eingebunden werden muss, wird sie über einen Lagrange-Multiplikator $\lambda$ an die Zielfunktion gekoppelt:

$$\mathcal{L}(\rho, \lambda) = C(\rho) + \lambda \cdot \left(\sum_e \rho_e \cdot v_e - V_{Ziel}\right)$$

$\lambda$ gewichtet dabei wie stark eine Volumenverletzung die Zielfunktion beeinflusst. Die Optimalitätsbedingung $\partial \mathcal{L} / \partial \rho_e = 0$ liefert dann direkt die Update-Regel für jede Dichte:

$$\rho_e^{new} = \rho_e \cdot \left(\frac{-\partial C / \partial \rho_e}{\lambda \cdot v_e}\right)^{0.5}$$

Der Exponent $0.5$ bzw. die Quadratwurzel dient als Dämpfungsfaktor der verhindert, dass die Dichten pro Iteration zu stark springen. 

Im Optimum ist der Steifigkeitsbeitrag pro Volumeneinheit für alle Elemente gleich, kein Element kann durch lokale Umverteilung von Material eine bessere Gesamtsteifigkeit erzeugen.
Die Update-Regel benötigt einen konkreten Wert für $\lambda$, dieser ist jedoch unbekannt und muss so gewählt werden, dass die Volumenbeschränkung nach dem Update exakt erfüllt ist. Da ein größeres $\lambda$ die Dichten senkt und ein kleineres sie erhöht, gibt es genau ein $\lambda^I$ das das Zielvolumen trifft. Dieses wird durch Bisektion gefunden: Der Algorithmus definiert ein weites Startintervall für $\lambda$ und halbiert es iterativ, bis $\lambda^I$ mit ausreichender Genauigkeit bestimmt ist. Der Prozess iteriert bis die maximale Dichteänderung erreicht ist.

# Beispiel mit Messerschmitt Bölkow–Blohm Balken
