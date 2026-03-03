from math import comb

# ========================
# UTILIDADES
# ========================

def fmt(p):
    return f"{p:.4g}"

def frecuencia_efectiva(m, n):
    return 2*m if n == 1 else m

def binomial_tail(k, r, p):
    if r <= 0:
        return 1.0
    if r > k:
        return 0.0
    return sum(comb(k, i) * p**i * (1-p)**(k-i) for i in range(r, k+1))

def prob_apuesta(m, n, v, t):
    s = len(v)
    k = t - s
    u = v.count(1)
    o = v.count(n)

    if n == 1:
        r = max(0, m - u)
        p = 1/6
    else:
        r = max(0, m - (o + u))
        p = 1/3

    return binomial_tail(k, r, p)

def prob_publica(m, n, s_sig, t):
    k = t - s_sig
    p = 1/6 if n == 1 else 1/3
    return binomial_tail(k, m, p)

def prob_siguiente_real(m, n, v, t, s_sig):
    s = len(v)
    u = v.count(1)
    o = v.count(n)

    p = 1/6 if n == 1 else 1/3
    k_rest = t - s - s_sig

    total = 0
    for y in range(s_sig + 1):
        prob_y = comb(s_sig, y) * p**y * (1-p)**(s_sig-y)
        r = max(0, m - (o + u) - y)
        prob_z = binomial_tail(k_rest, r, p)
        total += prob_y * prob_z

    return total

# ========================
# LÓGICA ESTRATÉGICA
# ========================

def analizar_apuesta(m, n, d, v, t):
    ef_ant = frecuencia_efectiva(m, n)
    max_prob = 0
    mejor_segura = None
    mejor_cercana = None
    min_diff = float("inf")

    for mb in range(1, t+1):
        for nb in range(1, 7):
            ef_nueva = frecuencia_efectiva(mb, nb)
            if ef_nueva < ef_ant or (ef_nueva == ef_ant and nb <= n):
                continue

            prob = prob_apuesta(mb, nb, v, t)

            if prob > max_prob:
                max_prob = prob
                mejor_segura = (mb, nb, prob)

            if prob >= d and prob - d < min_diff:
                min_diff = prob - d
                mejor_cercana = (mb, nb, prob)

    return mejor_segura, mejor_cercana

def maximizar_ventaja(m, n, d, v, t, s_sig):
    ef_ant = frecuencia_efectiva(m, n)
    mejor = None
    mejor_score = -1

    for mb in range(1, t+1):
        for nb in range(1, 7):
            ef_nueva = frecuencia_efectiva(mb, nb)
            if ef_nueva < ef_ant or (ef_nueva == ef_ant and nb <= n):
                continue

            prob_mia = prob_apuesta(mb, nb, v, t)
            if prob_mia < d:
                continue

            prob_sig = prob_publica(mb, nb, s_sig, t)
            score = prob_mia - prob_sig

            if score > mejor_score:
                mejor_score = score
                mejor = (mb, nb, prob_mia, prob_sig, score)

    return mejor

def modelo_bayesiano(m, n, d, v, t, s_sig):
    ef_ant = frecuencia_efectiva(m, n)
    mejor = None
    mejor_score = -1

    for mb in range(1, t+1):
        for nb in range(1, 7):
            ef_nueva = frecuencia_efectiva(mb, nb)
            if ef_nueva < ef_ant or (ef_nueva == ef_ant and nb <= n):
                continue

            prob_mia = prob_apuesta(mb, nb, v, t)
            if prob_mia < d:
                continue

            prob_sig = prob_siguiente_real(mb, nb, v, t, s_sig)
            score = prob_mia - prob_sig

            if score > mejor_score:
                mejor_score = score
                mejor = (mb, nb, prob_mia, prob_sig, score)

    return mejor

def probabilidad_cacho(m, n, v, t):
    s = len(v)
    k = v.count(n)
    u = t - s
    r = m - k

    if r < 0 or r > u:
        return 0
    return comb(u, r) * (1/6)**r * (5/6)**(u-r)

# ========================
# INPUT CENTRALIZADO
# ========================

def obtener_inputs():
    m = int(input("Frecuencia de la apuesta anterior: "))
    n = int(input("Número de la apuesta anterior: "))
    d = float(input("Probabilidad mínima aceptable (0-1): "))
    v = list(map(int, input("Tus dados (separados por comas): ").split(",")))
    t = int(input("Total de dados en mesa: "))
    s_sig = int(input("Dados del siguiente jugador: "))
    return m, n, d, v, t, s_sig

# ========================
# BLOQUES DE SALIDA
# ========================

def ejecutar_prediccion():
    m, n, d, v, t, s_sig = obtener_inputs()
    p = prob_apuesta(m, n, v, t)
    print(f"\nLa probabilidad de que la apuesta actual ({m} veces {n}) sea correcta es {fmt(p)}")

def ejecutar_mejor_apuesta():
    m, n, d, v, t, s_sig = obtener_inputs()
    segura, cercana = analizar_apuesta(m, n, d, v, t)

    if segura:
        mb, nb, p = segura
        print(f"\nLa apuesta más segura es {mb} veces {nb} con probabilidad {fmt(p)}")

    if cercana:
        mb, nb, p = cercana
        print(f"La apuesta más cercana al umbral {d} es {mb} veces {nb} con probabilidad {fmt(p)}")

def ejecutar_ventaja_clasica():
    m, n, d, v, t, s_sig = obtener_inputs()
    res = maximizar_ventaja(m, n, d, v, t, s_sig)

    if res:
        mb, nb, pm, ps, score = res
        print(f"\nLa apuesta que maximiza la ventaja clásica es {mb} veces {nb}")
        print(f"Tu probabilidad: {fmt(pm)}")
        print(f"Probabilidad pública del siguiente jugador: {fmt(ps)}")
        print(f"Ventaja estratégica: {fmt(score)}")

def ejecutar_ventaja_bayesiana():
    m, n, d, v, t, s_sig = obtener_inputs()
    res = modelo_bayesiano(m, n, d, v, t, s_sig)

    if res:
        mb, nb, pm, ps, score = res
        print(f"\nLa apuesta que maximiza la ventaja bayesiana es {mb} veces {nb}")
        print(f"Tu probabilidad real: {fmt(pm)}")
        print(f"Probabilidad real del siguiente jugador: {fmt(ps)}")
        print(f"Ventaja estratégica bayesiana: {fmt(score)}")

def ejecutar_cacho():
    m, n, d, v, t, s_sig = obtener_inputs()
    p = probabilidad_cacho(m, n, v, t)
    print(f"\nLa probabilidad exacta de que haya exactamente {m} veces {n} es {fmt(p)}")

def ejecutar_todo():
    m, n, d, v, t, s_sig = obtener_inputs()

    print("\n--- Análisis Completo ---")

    p_actual = prob_apuesta(m, n, v, t)
    print(f"\nProbabilidad actual de {m} veces {n}: {fmt(p_actual)}")

    segura, cercana = analizar_apuesta(m, n, d, v, t)

    if segura:
        print(f"\nMejor apuesta (seguridad): {segura[0]} veces {segura[1]} con probabilidad {fmt(segura[2])}")

    if cercana:
        print(f"Mejor apuesta (umbral): {cercana[0]} veces {cercana[1]} con probabilidad {fmt(cercana[2])}")

    res1 = maximizar_ventaja(m, n, d, v, t, s_sig)
    if res1:
        print(f"\nVentaja clásica máxima: {res1[0]} veces {res1[1]} (ventaja {fmt(res1[4])})")

    res2 = modelo_bayesiano(m, n, d, v, t, s_sig)
    if res2:
        print(f"Ventaja bayesiana máxima: {res2[0]} veces {res2[1]} (ventaja {fmt(res2[4])})")

    p_cacho = probabilidad_cacho(m, n, v, t)
    print(f"\nProbabilidad exacta de cacho: {fmt(p_cacho)}")

# ========================
# MENU
# ========================

def menu():
    opciones = {
        "1": ejecutar_prediccion,
        "2": ejecutar_mejor_apuesta,
        "3": ejecutar_ventaja_clasica,
        "4": ejecutar_ventaja_bayesiana,
        "5": ejecutar_cacho,
        "6": ejecutar_todo
    }

    print("""
          Elija la opción a ejecutar:
1 - Evaluar apuesta actual
2 - Mejor apuesta (seguridad y umbral)
3 - Maximizar ventaja clásica
4 - Maximizar ventaja bayesiana
5 - Probabilidad exacta de cacho
6 - Ejecutar análisis completo
""")

    eleccion = input("Selecciona una opción: ")

    if eleccion in opciones:
        opciones[eleccion]()
    else:
        print("Opción inválida")

menu()