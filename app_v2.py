import json
import os
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="App de Compras del Hogar", page_icon="🛒", layout="centered"
)

st.title("🛒 Lista de Mercado Compartida (Google Sheets)")


# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    try:
        # Intentamos leer de la variable de entorno primero (ideal para Render)
        json_str = os.environ.get("GCP_CREDENTIALS_JSON")

        if json_str:
            credentials_dict = json.loads(json_str)
        else:
            # Si no hay variable de entorno, intentamos usar st.secrets (ideal para local)
            credentials_dict = dict(st.secrets["gcp_service_account"])

        creds = Credentials.from_service_account_info(
            credentials_dict, scopes=scope
        )
        client = gspread.authorize(creds)
        sheet = client.open("base_datos_mercado").sheet1
        return sheet

    except Exception as e:
        st.error(f"Error crítico al conectar con Google Sheets: {e}")
        raise e


sheet = conectar_gsheets()  # Conexión a Google Sheets al inicio de la app


def cargar_datos_desde_sheets():
    registros = sheet.get_all_records()  # Retorna lista de diccionarios
    # Estructura base de tus 10 categorías
    datos = {
        "Frutas": [],
        "Verduras": [],
        "Carnes y pescado": [],
        "Lácteos": [],
        "Granos": [],
        "Cereales": [],
        "Legumbres": [],
        "Aceite, condimentos y endulzantes": [],
        "Aseo de hogar": [],
        "Aseo personal": [],
    }

    for row in registros:
        cat = row.get("Categoria")
        if cat in datos:
            # Convertir el valor de 'Comprado' de texto/booleano a booleano real de Python
            comprado_val = row.get("Comprado")
            if isinstance(comprado_val, str):
                comprado_bool = comprado_val.lower() == "true"
            else:
                comprado_bool = bool(comprado_val)

            datos[cat].append(
                {
                    "nombre": row.get("Nombre"),
                    "cantidad": row.get("Cantidad"),
                    "comprado": comprado_bool,
                }
            )
    return datos


# Función para sobrescribir toda la hoja con el estado actual de la app
def guardar_datos_en_sheets(lista_mercado):
    # Fila de encabezados
    filas = [["Categoria", "Nombre", "Cantidad", "Comprado"]]

    for cat, items in lista_mercado.items():
        for item in items:
            filas.append(
                [cat, item["nombre"], item["cantidad"], item["comprado"]]
            )

    sheet.clear()  # Limpia la hoja
    sheet.update(
        filas
    )  # Escribe todas las filas actualizadas de una vez en Google Sheets


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

# 2. Cargar estado inicial desde Google Sheets
if "lista_mercado" not in st.session_state:
    st.session_state.lista_mercado = cargar_datos_desde_sheets()

# 3. Selector de Rol en la barra lateral (Sidebar)
st.sidebar.header("👤 Selección de Usuario")
rol = st.sidebar.radio(
    "¿Quién está usando la app?",
    ["Usuario 1 (Registrar artículos)", "Usuario 2 (Ir al supermercado)"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Usuario 1:** Agrega, modifica o elimina (Sincronizado en Google Sheets).\n\n**Usuario 2:** Revisa cantidades y marca lo comprado."
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
                cant_def = (
                    "1 kg" if categoria_seleccionada == "Carnes y pescado" else 1
                )
                st.session_state.lista_mercado[categoria_seleccionada].append(
                    {"nombre": prod, "cantidad": cant_def, "comprado": False}
                )
            guardar_datos_en_sheets(st.session_state.lista_mercado)
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
                guardar_datos_en_sheets(st.session_state.lista_mercado)
                st.success(f"¡'{nuevo_articulo}' agregado!")
                st.rerun()
        else:
            st.error("Por favor ingresa un nombre válido.")

    st.markdown("---")

    # --- SECCIÓN C: MODIFICAR O ELIMINAR ARTÍCULOS EXISTENTES ---
    st.markdown("### ⚙️ Modificar cantidades o eliminar artículos")

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
                                    guardar_datos_en_sheets(
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
                                    guardar_datos_en_sheets(
                                        st.session_state.lista_mercado
                                    )

                        with cols[2]:
                            if st.button("🗑️ Borrar", key=f"del_{cat}_{idx}"):
                                items.pop(idx)
                                guardar_datos_en_sheets(
                                    st.session_state.lista_mercado
                                )
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
                            guardar_datos_en_sheets(
                                st.session_state.lista_mercado
                            )
                            st.rerun()
