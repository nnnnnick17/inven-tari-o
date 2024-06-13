import pandas as pd
import streamlit as st
import numpy as np
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt


#FUNCIONES
# Agregar Producto, verificar que tenga el codigo 6 digitos
def VerificarCodigo(x):
    if len(x) != 6:
        return False
    numeros = 0
    minusculas = 0
    for i in x:
        if i.isdigit():
            numeros += 1
        elif i.islower():
            minusculas += 1
    return numeros == 5 and minusculas == 1 #entrega true si es verdadero, por eso se pone directo

# Avisos de Stock, productos con stock bajo mostrarse
def AvisoStockBajo(x):
            if x == 0:
                return ("producto agotado")
            if x>0 and x <= 10:
                return ("producto extremadamente bajo, casi agotado")
            elif x> 10 and x <= 30:
                return ("producto excesivamente bajo")
            elif x> 30 and x <= 50:
                return ("producto bajo")
            else:
                return ""

# Analisis Ventas, grafico tendencia ventas
def GraficoTendenciaVentas(arch_ventas):
    if not arch_ventas.empty:
        # convertir la columna de fecha a datetime
        arch_ventas["Fecha"] = pd.to_datetime(arch_ventas["Fecha"])
        # agrupar por fecha y sumar las ventas
        ventas_por_fecha = arch_ventas.groupby("Fecha")["Cantidad Vendida"].sum().reset_index()
        # grafico matplotlib
        plt.figure(figsize=(15, 10))
        plt.plot(ventas_por_fecha["Fecha"], ventas_por_fecha["Cantidad Vendida"])
        plt.xlabel("Fecha")
        plt.ylabel("Cantidad Vendida")
        st.pyplot(plt)
# analisis ventas, producto mas vendido
def ProductoMasVendido (arch_ventas):
    if not arch_ventas.empty:
        productos_mas_vendidos = arch_ventas.groupby("Producto")["Cantidad Vendida"].sum().sort_values(ascending=False)
        st.bar_chart(productos_mas_vendidos)
#analisis ventas, informe ventas
def InformeVentas (arch_ventas):
    if not arch_ventas.empty:
        arch_ventas["Fecha"] = pd.to_datetime(arch_ventas["Fecha"]) #columna de fecha a tipo datetime
        arch_ventas["Mes"] = arch_ventas["Fecha"].dt.month.map({1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"})
        arch_ventas["Año"] = arch_ventas["Fecha"].dt.year
        #agrupar por mes y sumar las ventas
        ventas_por_mes = arch_ventas.groupby(["Año", "Mes"])["Cantidad Vendida"].sum().reset_index()
        #tener una tabla con meses como filas y años como columnas
        pivot_ventas = ventas_por_mes.pivot_table(index="Mes", columns="Año", values="Cantidad Vendida", aggfunc="sum", fill_value=0)
        #se agrega una fila al final para la suma de las ventas mensuales por año
        pivot_ventas.loc["Total Anual"] = pivot_ventas.sum()
        st.dataframe(pivot_ventas)


# CONFIGURACION PAGINA
if True:
    #general
    st.set_page_config( 
        page_title="ManejoInventario", #titulo
        page_icon="icon.png", #icono
        layout="centered",
        initial_sidebar_state="auto"
        )
    #barra lateral
    st.sidebar.image("icon.png", width=75,)
    with st.sidebar:
        selected = option_menu("MANEJO INVENTARIO: TIENDA MINORISTA", ["Agregar Producto", "Modificar Producto", "Eliminar Producto", "Inventario", "Avisos de Stock", "Registrar Venta", "Historial Ventas", "Analisis Ventas", "Restablecer Inventario e Historial"], 
            icons=["plus-circle-fill", "wrench-adjustable-circle-fill", "trash-fill", "box2-fill", "alarm-fill", "cash-coin", "clipboard-data", "file-bar-graph-fill", "exclamation-triangle-fill"], menu_icon="shop", default_index=0)

# Cargamos el archivo EXCEL INVENTARIO
if True:
    try:
        arch_inventario = pd.read_excel("Inventario.xlsx")
    except FileNotFoundError:
        st.error("No posee inventario, el archivo ""Inventario.xlsx"" no se encuentra. Si desea crearlo siga con el curso y registre un producto.")
        arch_inventario = pd.DataFrame(columns=["Producto","Código", "Cantidad", "Precio C/U", "Precio Total"])  # crear un dataframe vacio si no existe el archivo
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# Cargamos el archivo EXCEL DE HISTORIAL VENTAS
if True:
    try:
        arch_ventas = pd.read_excel("HistorialVentas.xlsx")
    except FileNotFoundError:
        st.error("No posee un historial de ventas, el archivo ""HistorialVentas.xlsx"" no se encuentra. Si desea crearlo siga con el curso y registre una venta.")
        arch_ventas = pd.DataFrame(columns=["Fecha", "Producto", "Código", "Cantidad Vendida", "Precio C/U", "Precio Total"])  # crear un dataframe vacio si no existe el archivo
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")


#PAGINA    
if selected == "Agregar Producto":
    st.title("Agregar Producto a Inventario")
    producto = st.text_input("Nombre del Producto")
    codigo = st.text_input("Código [6 digitos]: [5 números] [1 letra minuscula]")
    cantidad = st.number_input("Cantidad", min_value=0)
    precio_unitario = st.number_input("Precio C/U", min_value=0)
    
    if st.button("Agregar al Inventario"):
        if producto and cantidad > 0 and precio_unitario > 0 and VerificarCodigo(codigo):
            if producto in arch_inventario["Producto"].values: # ver si el producto ya existe en el inventario
                codigo_existente = arch_inventario.loc[arch_inventario["Producto"] == producto, "Código"].values[0] # producto existente, entonces verificar el codigo
                indic = arch_inventario.index[arch_inventario["Producto"] == producto][0]
                if codigo == codigo_existente:
                    # al añadir producto, calcular nuevo precio promediado con el anterior
                    cantidad_existente = arch_inventario.loc[indic, "Cantidad"]
                    precio_unitario_existente = arch_inventario.loc[indic, "Precio C/U"]
                    precio_total_existente = arch_inventario.loc[indic, "Precio Total"]
                    nuevo_precio_total = precio_unitario * cantidad
                    nueva_cantidad_total = cantidad_existente + cantidad
                    nuevo_precio_total_producto_entero = precio_total_existente + nuevo_precio_total
                    nuevo_precio_unitario_promediado = (precio_total_existente + nuevo_precio_total) / nueva_cantidad_total
                    # actualizar los datos
                    arch_inventario.loc[indic, "Cantidad"] = nueva_cantidad_total
                    arch_inventario.loc[indic, "Precio C/U"] = nuevo_precio_unitario_promediado
                    arch_inventario.loc[indic, "Precio Total"] = nuevo_precio_total_producto_entero
                    arch_inventario.to_excel("Inventario.xlsx", index=False)  # Guardar en el archivo Excel
                    st.success(f"Cantidad de [{producto}] actualizada correctamente en el inventario.")
                else:
                    # codigo no coincide
                    st.error(f"El producto [{producto}] ya existe en el inventario pero con un código diferente")
            elif codigo in arch_inventario["Código"].values:
                st.error("El codigo ya está asociado a otro producto en el inventario")
            else: #agregar producto, no existente
                precio_total = cantidad * precio_unitario # añadir precio total
                # agregar los datos al dataframe
                nuevo_producto = pd.DataFrame({
                    "Producto": [producto],
                    "Código": [codigo],
                    "Cantidad": [cantidad],
                    "Precio C/U": [precio_unitario],
                    "Precio Total": [precio_total]
                })
                arch_inventario = pd.concat([arch_inventario, nuevo_producto], ignore_index=True)
                arch_inventario.to_excel("Inventario.xlsx", index=False)  #guardado en el archivo excel
                st.success(f"Producto [{producto}] [{codigo}] agregado al inventario correctamente.")
        elif VerificarCodigo(codigo) == False:
            st.error ("Por favor, introducir correctamente la cantidad de digitos en el codigo.")
        else:
            st.error("Por favor, complete todos los campos correctamente.")

elif selected == "Inventario":
    st.title("Inventario Actual")
    if not arch_inventario.empty:
        st.text("""En la esquina superior derecha del cuadro/inventario puede:
1) Descargar formato CSV
2) Buscar en especifico cierto producto o identificador
3) Agrandar el cuadro/inventario""")
        st.divider()
        st.dataframe(arch_inventario)
        precio_total_inventario = arch_inventario["Precio Total"].sum()
        st.text (f"Ël precio total del inventario es de ${precio_total_inventario} CLP")
    else:
        st.warning("No hay informacion en el inventario")

elif selected == "Modificar Producto":
    st.title("Modificar Producto Del Inventario")
    if arch_inventario.empty: 
        st.warning("No hay información en el inventario")
    else:
        st.text("Para mantener valor escribirlo nuevamente")
        producto = st.selectbox("Seleccione o Busque el Producto", arch_inventario["Producto"].unique())
        nuevo_nombre =st.text_input ("Nuevo Nombre")
        nuevo_codigo = st.text_input ("Nuevo Código [6 digitos]: [5 números] [1 letra minuscula]")
        nueva_cantidad = st.number_input ("Nueva Cantidad", min_value=0)
        nuevo_precio_unitario = st.number_input ("Nuevo Precio C/U", min_value=0)

        if st.button("Actualizar"):
            if nueva_cantidad > 0 and nuevo_precio_unitario > 0 and VerificarCodigo(nuevo_codigo):
                arch_inventario.loc[arch_inventario["Producto"] == producto, "Producto"] = nuevo_nombre
                arch_inventario.loc[arch_inventario["Producto"] == producto, "Cantidad"] = nueva_cantidad
                arch_inventario.loc[arch_inventario["Producto"] == producto, "Precio C/U"] = nuevo_precio_unitario
                arch_inventario.loc[arch_inventario["Producto"] == producto, "Código"] = nuevo_codigo
                arch_inventario.loc[arch_inventario["Producto"] == producto, "Precio Total"] = nueva_cantidad * nuevo_precio_unitario
                nuevo_precio_total = nueva_cantidad * nuevo_precio_unitario
                try:
                    arch_inventario.to_excel("Inventario.xlsx", index=False)  #guardando en el archivo Excel
                    st.success(f"[{producto}] [{nuevo_codigo}] actualizado/a correctamente.")
                except Exception as e:
                    st.error(f"Error al guardar en el archivo Excel: {e}")
            elif VerificarCodigo(nuevo_codigo)==False:
                st.error ("Por favor, introducir correctamente la cantidad de digitos en el codigo")
            else:
                st.error("Por favor, complete todos los campos correctamente")

elif selected == "Eliminar Producto":
    st.title("Eliminar Producto del Inventario")
    if arch_inventario.empty: 
        st.warning("No hay información en el inventario")
    else:
        producto = st.selectbox("Seleccione o Busque el Producto", arch_inventario["Producto"].unique())
        codigo = arch_inventario.loc[arch_inventario["Producto"] == producto, "Código"].values[0]
        
        if st.button("Eliminar"):
            arch_inventario = arch_inventario[arch_inventario["Producto"] != producto]
            try:
                arch_inventario.to_excel("Inventario.xlsx", index=False)  # guardando en el archivo excel
                st.success(f"Producto [{producto}] [{codigo}] eliminado del inventario.")
            except Exception as e:
                st.error(f"Error al guardar en el archivo Excel: {e}")

elif selected == "Avisos de Stock":
    st.title("Avisos de Stock del Inventario")
    if arch_inventario.empty: 
        st.warning("No hay información en el inventario")
    else:
        st.text("""Recordar: 
Cantidad = 0: "producto agotado"
Cantidad = 1-10: "producto proximo a acabarse"
Cantidad = 11-30: "producto con poco stock"
Cantidad = 31-50: "producto bajo\"""")
        arch_inventario["Aviso"] = arch_inventario["Cantidad"].apply(AvisoStockBajo) #cada columna de cantidad
        
        #mostrar producto con cualquier tipo de aviso
        productos_con_aviso = arch_inventario[arch_inventario["Aviso"] != ""]
        st.divider()
        if not productos_con_aviso.empty:
            st.dataframe(productos_con_aviso)
        else:
            st.text("No hay productos con avisos de stock")

elif selected == "Registrar Venta":
    st.title("Registrar Venta Tienda")
    if arch_inventario.empty:
        st.warning("No hay informacion en el inventario para concretar una venta")
    else:
        producto_vendido = st.selectbox("Producto Vendido", arch_inventario["Producto"].unique())
        cantidad_vendida = st.number_input("Cantidad Vendida", min_value=0)
        cantidad_producto_arch=arch_inventario.loc[arch_inventario["Producto"] == producto_vendido, "Cantidad"].values[0]
        precio_unitario = arch_inventario.loc[arch_inventario["Producto"] == producto_vendido, "Precio C/U"].values[0]
        codigo = arch_inventario.loc[arch_inventario["Producto"] == producto_vendido, "Código"].values[0] #para mostrar el codigo luego

        if st.button("Registrar Venta"):
            if cantidad_vendida <= cantidad_producto_arch:
                arch_inventario.loc[arch_inventario["Producto"] == producto_vendido, "Cantidad"] -= cantidad_vendida #actualizar cantidad del producto
                precio_total_venta = cantidad_vendida * precio_unitario # no actualiza el precio total, es el precio total de venta
                
                # Crear historial de venta
                nueva_venta = pd.DataFrame({
                    "Fecha": [pd.Timestamp.now()], #para analisis posterior
                    "Producto": [producto_vendido],
                    "Código": [codigo],
                    "Cantidad Vendida": [cantidad_vendida],
                    "Precio Unitario": [precio_unitario],
                    "Precio Total": [precio_total_venta]})
                
                if arch_ventas.empty:
                    arch_ventas = nueva_venta
                else:
                    arch_ventas = pd.concat([arch_ventas, nueva_venta], ignore_index=True)
                
                try:
                    arch_inventario["Precio Total"] = arch_inventario["Cantidad"] * arch_inventario["Precio C/U"]
                    arch_inventario.to_excel("Inventario.xlsx", index=False)  #guardando en el excel
                    arch_ventas.to_excel("HistorialVentas.xlsx", index=False)
                    st.success(f"Venta de [{cantidad_vendida}] de [{producto_vendido}][{codigo}] registrada exitosamente.")
                except Exception as e:
                    st.error(f"Error al guardar en el archivo Excel: {e}")
            else:
                st.error("No hay suficiente cantidad disponible en el inventario para esta venta")
       
elif selected == "Historial Ventas":
    st.title("Historial de Ventas")
    if arch_ventas.empty:
        st.warning("No hay ventas registradas")
    else:
        st.text("""En la esquina superior derecha del cuadro puede:
1) Descargar formato CSV
2) Buscar en específico cierto producto o identificador
3) Agrandar el cuadro""")
        arch_ventas["Fecha"] = pd.to_datetime(arch_ventas["Fecha"])
        arch_ventas = arch_ventas.sort_values(by="Fecha", ascending=False) # ordenar el dataframe al reves, fechas actuales al inicio y las que comenzaron al final
        st.dataframe(arch_ventas)

elif selected == "Analisis Ventas":
    st.title("Análisis de Ventas")
    if arch_ventas.empty:
        st.warning ("No hay datos de ventas para mostrar")
    else:
        st.text ("""Escoger Analisis:
1) Tendencia de Ventas
2) Producto Mas Vendido
3) Informe de Ventas""")
        selected2 = option_menu(None, ["Tendencia Ventas", "Producto Mas Vendido", "Informe Ventas"]
                                , orientation="horizontal")
        
        # grafico de tendencia de ventas a lo largo del tiempo
        if selected2 == "Tendencia Ventas":
            GraficoTendenciaVentas(arch_ventas)

        # analisis de productos mas vendidos
        elif selected2 == "Producto Mas Vendido":
            ProductoMasVendido(arch_ventas)
        # informe de ventas
        elif selected2 == "Informe Ventas":
            InformeVentas(arch_ventas)

elif selected == "Restablecer Inventario e Historial":
    st.title("Restablecer Inventario e Historial Tienda")
    if arch_inventario.empty and arch_ventas.empty: 
        st.warning("No hay información en el inventario e historial")
    else:
        st.markdown(""":red[NO SE PODRA RECUPERAR DE NINGUNA FORMA LA DECISION]""")
        seleccion_si_no = st.selectbox("Estás seguro?", ("si", "no"), index=None, placeholder="")
        st.text("")
        st.text("")
        if seleccion_si_no == "si":
            if st.button("Último Paso: Apretar para restablecer inventario"):
                arch_inventario = pd.DataFrame(columns=["Producto","Código", "Cantidad", "Precio C/U", "Precio Total"])
                arch_ventas = pd.DataFrame(columns=["Fecha", "Producto", "Código", "Cantidad Vendida", "Precio C/U", "Precio Total"])
                try:
                    arch_inventario.to_excel("Inventario.xlsx", index=False)  #guardando en el archivo Excel
                    arch_ventas.to_excel("HistorialVentas.xlsx", index=False) #guardando historial ventas
                    st.success("El inventario ha sido restablecido exitosamente.")
                except Exception as e:
                    st.error(f"Error al guardar en el archivo Excel: {e}")
        elif seleccion_si_no == "no":
            st.text("")

