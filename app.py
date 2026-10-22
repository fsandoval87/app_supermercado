import json
import os
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="App de Compras del Hogar", page_icon="🛒", layout="centered"
)

st.title("🛒 Lista de Mercado Compartida")

# Nombre del archivo donde se guardarán los datos de forma persistente
ARCHIVO_DATOS = "datos_mercado.json"


# Funciones para cargar y guardar en JSON
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Si el archivo está corrupto o vacío, devolvemos la estructura por defecto
            return None
    return None


def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


# 1. Catálogo completo de artículos comunes por categoría
if "catalogo_comun" not in st.session_state:
    st.session_state.catalogo_comun = {
        "Frutas": [
            "Manzanas verdes",
            "Manzanas rojas",
            "Bananos",
            "Granadillas",
            "Papaya",
            "Mangos",
            "Uvas",
            "Peras",
            "Piña",
            "Pitahaya",
            "Fresas",
            "Arándanos",
            "Limones",
        ],
        "Verduras": [
            "Aguacates",
            "Tomates",
            "Cebolla blanca",
            "Cebolla morada",
            "Cebolla larga",
            "Lechuga",
            "Zanahorias",
            "Apio",
            "Espinaca",
            "Papa",
            "Yuca",
            "Cilantro",
            "Perejil",
            "Pimentón",
            "Brócoli",
            "Coliflor",
            "Pepino cohombro",
            "Zucchini",
            "Ahuyama",
            "Remolacha",
            "Berenjena",
        ],
        "Carnes y pescado": [
            "Pechuga de pollo",
            "Carne de res para asar",
            "Carne de res para desmechar",
            "Carne molida de res",
            "Atún enlatado en agua",
            "Jamón de pollo",
            "Jamón de cerdo",
            "Salchichas",
            "Chorizos",
            "Salmón",
            "Trucha",
        ],
        "Lácteos": [
            "Leche",
            "Queso mozarella",
            "Queso crema",
            "Queso cuajada",
            "Queso parmesano",
            "Queso crema",
            "Yogur griego",
            "Mantequilla",
            "Crema de leche",
            "Huevos",
        ],
        "Granos": ["Arroz", "Frijoles", "Garbanzos", "Lentejas", "Maíz pira", "Blanquillos"],
        "Cereales": ["Avena", "Granola", "Harina de maíz", "Pasta", "Harina de trigo", "Quinua", "Linaza", "Chía"],
        "Legumbres": ["Arvejas secas", "Soya texturizada"],
        "Aceite, condimentos y endulzantes": [
            "Aceite de oliva",
            "Aceite de aguacate",
            "Sal",
            "Pimienta",
            "Azúcar",
            "Panela",
            "Vinagre",
        ],
        "Aseo de hogar": [
            "Jabón loza",
            "Detergente líquido de ropa",
            "Limpiador multiusos",
            "Blanqueador en gel",
            "Bolsas de basura",
            "Esponjas",
            "Limpiavidrios",
        ],
        "Aseo personal": [
            "Jabón de baño",
            "Crema dental",
            "Shampoo",
            "Desodorante",
            "Papel higiénico",
        ],
    }

# 2. Inicializar el estado de la lista cargando desde el JSON (o creando uno por defecto si no existe)
if "lista_mercado" not in st.session_state:
    datos_cargados = cargar_datos()
    if datos_cargados is not None:
        st.session_state.lista_mercado = datos_cargados
    else:
        # Estructura inicial por defecto si el archivo no existe
        st.session_state.lista_mercado = {
            "Frutas": [
                {"nombre": "Manzanas verdes", "cantidad": 4, "comprado": False},
                {"nombre": "Bananos", "cantidad": 8, "comprado": False},
                {"nombre": "Arándanos", "cantidad": 2, "comprado": False}
            ],
            "Verduras": [
                {"nombre": "Tomates", "cantidad": 5, "comprado": False},
                {"nombre": "Cebolla morada", "cantidad": 3, "comprado": False}
            ],
            "Carnes y pescado": [
                {"nombre": "Carne molida de res",
                    "cantidad": "1 kg", "comprado": False}
            ],
            "Lácteos": [{"nombre": "Queso cuajada", "cantidad": 2, "comprado": False}],
            "Granos": [],
            "Cereales": [],
            "Legumbres": [],
            "Aceite, condimentos y endulzantes": [],
            "Aseo de hogar": [],
            "Aseo personal": [],
        }
        guardar_datos(st.session_state.lista_mercado)

# 3. Selector de Rol en la barra lateral (Sidebar)
st.sidebar.header("👤 Selección de Usuario")
rol = st.sidebar.radio(
    "¿Quién está usando la app?",
    ["Usuario 1 (Registrar artículos)", "Usuario 2 (Ir al supermercado)"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Usuario 1:** Agrega, modifica cantidades o elimina artículos (Guardado automático).\n\n**Usuario 2:** Revisa cantidades y marca lo comprado."
)

# ==========================================
# VISTA: USUARIO 1 (Agregar, Modificar y Eliminar)
# ==========================================
if rol == "Usuario 1 (Registrar artículos)":
    st.header("📝 Gestión de la Lista de Compras")

    categoria_seleccionada = st.selectbox(
        "Selecciona la categoría", list(st.session_state.lista_mercado.keys())
    )

    # --- SECCIÓN A: SELECCIÓN RÁPIDA ---
    st.markdown("### ⚡ Selección rápida de comunes")
    nombres_actuales = [
        item["nombre"]
        for item in st.session_state.lista_mercado[categoria_seleccionada]
    ]
    opciones_disponibles = [
        item
        for item in st.session_state.catalogo_comun.get(
            categoria_seleccionada, []
        )
        if item not in nombres_actuales
    ]

    seleccionados_rapidos = st.multiselect(
        "Artículos frecuentes:", opciones_disponibles
    )

    if st.button("Agregar selección rápida"):
        if seleccionados_rapidos:
            for prod in seleccionados_rapidos:
                cant_def = "1 kg" if categoria_seleccionada == "Carnes y pescado" else 1
                st.session_state.lista_mercado[categoria_seleccionada].append(
                    {"nombre": prod, "cantidad": cant_def, "comprado": False}
                )
            # Guardar cambios en el archivo JSON
            guardar_datos(st.session_state.lista_mercado)
            st.success(
                f"¡Se agregaron {len(seleccionados_rapidos)} artículos!")
            st.rerun()
        else:
            st.warning("No has seleccionado ningún artículo.")

    st.markdown("---")

    # --- SECCIÓN B: ARTÍCULO ESPECÍFICO ---
    st.markdown("### ✍️ O añade un artículo específico")
    col1, col2 = st.columns([2, 1])
    with col1:
        nuevo_articulo = st.text_input("Nombre del artículo:")
    with col2:
        if categoria_seleccionada == "Carnes y pescado":
            cantidad_articulo = st.text_input("Cantidad:", value="1 kg")
        else:
            cantidad_articulo = st.number_input(
                "Unidades:", min_value=1, step=1, value=1
            )

    if st.button("Agregar artículo específico"):
        if nuevo_articulo.strip() != "":
            nombres_existentes = [
                item["nombre"].lower()
                for item in st.session_state.lista_mercado[categoria_seleccionada]
            ]
            if nuevo_articulo.strip().lower() in nombres_existentes:
                st.warning(
                    "¡Este artículo ya está en la lista de esa categoría!")
            else:
                st.session_state.lista_mercado[categoria_seleccionada].append(
                    {
                        "nombre": nuevo_articulo.strip(),
                        "cantidad": cantidad_articulo,
                        "comprado": False,
                    }
                )
                # Guardar cambios en el archivo JSON
                guardar_datos(st.session_state.lista_mercado)
                st.success(f"¡'{nuevo_articulo}' agregado!")
                st.rerun()
        else:
            st.error("Por favor ingresa un nombre válido.")

    st.markdown("---")

    # --- SECCIÓN C: MODIFICAR O ELIMINAR ARTÍCULOS EXISTENTES ---
    st.markdown("### ⚙️ Modificar cantidades o eliminar artículos")
    st.markdown(
        "Aquí puedes corregir cantidades o borrar artículos ingresados por error:"
    )

    hay_articulos_totales = any(
        items for items in st.session_state.lista_mercado.values()
    )

    if not hay_articulos_totales:
        st.info("No hay artículos en ninguna categoría actualmente.")
    else:
        for cat, items in st.session_state.lista_mercado.items():
            if items:
                with st.expander(f"📁 {cat} ({len(items)} items registrados)"):
                    for idx, item in enumerate(items):
                        cols = st.columns([2, 2, 1])

                        with cols[0]:
                            estado_txt = (
                                " *(Comprado)*" if item["comprado"] else ""
                            )
                            st.markdown(f"**{item['nombre']}**{estado_txt}")

                        with cols[1]:
                            if cat == "Carnes y pescado":
                                nueva_cant = st.text_input(
                                    "Cant",
                                    value=str(item["cantidad"]),
                                    key=f"edit_cant_{cat}_{idx}",
                                    label_visibility="collapsed",
                                )
                                if nueva_cant != item["cantidad"]:
                                    item["cantidad"] = nueva_cant
                                    guardar_datos(
                                        st.session_state.lista_mercado
                                    )
                            else:
                                val_actual = (
                                    int(item["cantidad"])
                                    if isinstance(item["cantidad"], int)
                                    else 1
                                )
                                nueva_cant = st.number_input(
                                    "Unids",
                                    min_value=1,
                                    step=1,
                                    value=val_actual,
                                    key=f"edit_cant_{cat}_{idx}",
                                    label_visibility="collapsed",
                                )
                                if nueva_cant != item["cantidad"]:
                                    item["cantidad"] = nueva_cant
                                    guardar_datos(
                                        st.session_state.lista_mercado
                                    )

                        with cols[2]:
                            if st.button("🗑️ Borrar", key=f"del_{cat}_{idx}"):
                                items.pop(idx)
                                guardar_datos(st.session_state.lista_mercado)
                                st.rerun()

# ==========================================
# VISTA: USUARIO 2 (Supermercado)
# ==========================================
else:
    st.header("🛒 Compras en el Supermercado")
    st.markdown(
        "Revisa la cantidad necesaria y marca los productos a medida que los pongas en el carrito."
    )

    hay_productos = any(
        not item["comprado"]
        for items in st.session_state.lista_mercado.values()
        for item in items
    )

    if not hay_productos:
        st.success(
            "🎉 ¡No hay pendientes en la lista de mercado! Todo está comprado."
        )
    else:
        for cat, items in st.session_state.lista_mercado.items():
            pendientes = [item for item in items if not item["comprado"]]

            if pendientes:
                st.subheader(f"📌 {cat}")
                for item in items:
                    if not item["comprado"]:
                        if isinstance(item["cantidad"], int):
                            texto_checkbox = f"**{item['nombre']}** — 📦 *Unidades: {item['cantidad']}*"
                        else:
                            texto_checkbox = f"**{item['nombre']}** — 📦 *Cantidad: {item['cantidad']}*"

                        comprado = st.checkbox(
                            texto_checkbox,
                            key=f"chk_{cat}_{item['nombre']}",
                        )
                        if comprado:
                            item["comprado"] = True
                            # Guardar inmediatamente al marcar como comprado
                            guardar_datos(st.session_state.lista_mercado)
                            st.rerun()
