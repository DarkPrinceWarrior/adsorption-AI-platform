import base64

import streamlit
from streamlit_option_menu import option_menu
from components.page_team_contact import contact_action, team_action
from components.page_mof_information import mof_inf_action
from components.predict import predict


streamlit.set_page_config(
    layout="wide",
    page_title="adsorption AI platform",
    initial_sidebar_state="collapsed"
)

with open("static/style.css") as css_file:
    streamlit.markdown('<style>{}</style>'.format(css_file.read()), unsafe_allow_html=True)


@streamlit.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("images/background.jpg")

page_back = f"""
<style>

[data-testid="stAppViewContainer"]{{
background-image: url("data:image/png;base64,{img}");
# background-image: url("../images/background.jpg");
background-size: cover;
}}
</style>
"""

streamlit.markdown(page_back, unsafe_allow_html=True)


def predict_action():
    streamlit.title("Предсказание методики синтеза MOFs")

    page_style = f"""
    <style>
    .css-7mza0f {{
        border:3px solid white;
        padding:10px;
        background-color: white;
    }}
    </style>
    """

    streamlit.markdown(page_style, unsafe_allow_html=True)
    Temp_reg_C = streamlit.number_input("Tрег, ᵒС - температура регенерации",value=200)
    W0_cm3_g = streamlit.number_input("W0, см3/г - удельный объем микропор",value=0.65)
    E0_KDG_moll = streamlit.number_input("E0, кДж/ моль - энергия адсорбции бензола",value=24.15)
    x0_nm = streamlit.number_input("х0, нм - радиус микропор",value=0.50)
    a0_mmoll_gr = streamlit.number_input("а0, ммоль/г - предельная величина адсорбции",value=18.59)
    E_kDg_moll = streamlit.number_input("E,  кДж/моль - энергия адсорбции азота",value=7.97)
    SBAT_m2_gr = streamlit.number_input("SБЭТ, м2/г - удельная площадь поверхности",value=1473.00)
    Ws_cm3_gr = streamlit.number_input("Ws, см3/г - суммарный объем пор",value=0.68)
    Sme_m2_gr = streamlit.number_input("Sme, м2/г - площадь поверхности мезопор",value=22.00)
    Wme_cm3_gr = streamlit.number_input("Wme, см3/г - объем мезопор",value=0.03)

    data = {
        "Regeneration temperature of the sample, °C": Temp_reg_C,
        "Specific volume of micropores, cm3/g": W0_cm3_g,
        "Standard characteristic energy of benzene adsorption, kJ/mol": E0_KDG_moll,
        "Mean effective half-width of micropores, nm": x0_nm,
        "Ultimate adsorption value of nitrogen in micropores, mmol/g": a0_mmoll_gr,
        "Characteristic energy of nitrogen adsorption, kJ/mol": E_kDg_moll,
        "Specific surface area, m2/g": SBAT_m2_gr,
        "Total pore volume, cm3/g": Ws_cm3_gr,
        "Mesopore surface area, m2/g": Sme_m2_gr,
        "Mesopore volume, cm3/g": Wme_cm3_gr
    }

    if streamlit.button("Отправить на анализ и получить методику синтеза"):
        table_params, prediction_table = predict(data)
        streamlit.title("Структурно энергетические характеристики MOFs:")
        prediction_table.columns = ["Металл",
                                    "Лиганд",
                                    "n(соль)/n(кислота)",
                                    "Vсин(р-ля)/m(соли)",
                                    "Т.син."]
        streamlit.table(table_params)
        streamlit.title("Сгенерированные параметры методики синтеза MOFs:")
        streamlit.table(prediction_table)


def run():
    with streamlit.sidebar:
        selected = option_menu(
            menu_title="𝐀𝐈 сервис пористых материалов",
            options=["О нас", "MOFs описание", "𝐀𝐈 синтез MOFs", "Контакты"],
            icons=["house", "book", "box fill", "list task", "person lines fill",
                   # "clipboard data fill",
                   "bar-chart-line-fill"],
            menu_icon="kanban fill",
            default_index=0,
            # orientation="horizontal",
            styles={
                "container": {"padding": "0 % 0 % 0 % 0 %"},
                "icon": {"color": "red", "font-size": "25px"},
                "nav-link": {"font-size": "20px", "text-align": "start", "margin": "0px"},
                "nav-link-selected": {"background-color": "#483D8B"},
            }

        )

    if selected == "О нас":
        team_image = "images/team.jpg"
        team_action(team_image)
    if selected == "𝐀𝐈 синтез MOFs":
        predict_action()
    if selected == "MOFs описание":
        image1 = "images/1page.jpg"
        image2 = "images/2page.jpg"
        mof_inf_action(image1, image2)
    if selected == "Контакты":
        contact_action()


if __name__ == '__main__':
    run()
