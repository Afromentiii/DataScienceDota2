def znajdz_duplikaty(linie):
    wystapienia = {}
    duplikaty = []

    for idx, linia in enumerate(linie):
        if linia in wystapienia:
            wystapienia[linia].append(idx)
        else:
            wystapienia[linia] = [idx]

    for linia, indeksy in wystapienia.items():
        if len(indeksy) > 1:
            duplikaty.append((linia, indeksy))

    return duplikaty


with open("data2.csv", encoding="utf-8") as f:
    linie = [linia.strip() for linia in f if linia.strip()]

duplikaty = znajdz_duplikaty(linie)

if duplikaty:
    print("Znaleziono duplikaty:")
    for linia, indeksy in duplikaty:
        numery_linii = [i + 1 for i in indeksy]
        print(f"Linia: '{linia}' pojawia się na liniach: {numery_linii}")
else:
    print("Brak duplikatów.")
