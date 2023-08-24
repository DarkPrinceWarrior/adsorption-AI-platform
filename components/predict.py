import pickle

import numpy as np
import pandas as pd
import pymatgen.core as mg
from rdkit import Chem
from rdkit.Chem import Lipinski, Descriptors, MolSurf

pkl_filename = "saved_models/model_met.pkl"
with open(pkl_filename, 'rb') as file:
    model_met = pickle.load(file)

pkl_filename = "saved_models/model_lig.pkl"
with open(pkl_filename, 'rb') as file:
    model_lig = pickle.load(file)

pkl_filename = "saved_models/model_salt_acid.pkl"
with open(pkl_filename, 'rb') as file:
    model_salt_acid = pickle.load(file)

pkl_filename = "saved_models/model_solv_salt.pkl"
with open(pkl_filename, 'rb') as file:
    model_solv_salt = pickle.load(file)

pkl_filename = "saved_models/model_temp_synth.pkl"
with open(pkl_filename, 'rb') as file:
    model_temp_synth = pickle.load(file)


def convert_to_smiles(ligand_name):
    if ligand_name == "BTC":
        return 'C1=CC(=C(C=C1C(=O)O)C(=O)O)C(=O)O'
    elif ligand_name == "BDC":
        return 'C1=CC(=CC=C1C(=O)O)C(=O)O'
    elif ligand_name == "NH2-BDC":
        return 'C1=CC(=C(C=C1C(=O)O)N)C(=O)O'
    else:
        return 'OC(=O)c1ccc(cc1)-c2cc(cc(c2)-c3ccc(cc3)C(O)=O)-c4ccc(cc4)C(O)=O'


def predict(data):
    values = list(data.values())
    df = pd.DataFrame(data=np.array(values).reshape(1, -1),
                      columns=list(data.keys()))

    metal = model_met.predict(df)
    df["metal"] = metal

    # metal descriptors
    df['Total molecular weight (metal)'] = mg.Composition(metal[0][0]).weight
    df['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal[0][0]).elements[0]).average_ionic_radius
    df['Average electronegativity (metal)'] = mg.Composition(metal[0][0]).average_electroneg

    ligand = model_lig.predict(df[[x for x in df.columns if x != "metal"]])
    df["ligand"] = ligand
    # столбец smiles у лигандов
    df['ligand_smiles'] = df['ligand'].apply(lambda x: convert_to_smiles(x))

    df['Number of Hydrogen Bond Donors'] = df['ligand_smiles'].apply(
        lambda x: Lipinski.NumHDonors(Chem.MolFromSmiles(x)))
    df['Number of Hydrogen Bond Acceptors'] = df['ligand_smiles'].apply(
        lambda x: Lipinski.NumHAcceptors(Chem.MolFromSmiles(x)))
    df['The exact molecular weight of the molecule, g/mol'] = df['ligand_smiles'].apply(
        lambda x: Descriptors.ExactMolWt(Chem.MolFromSmiles(x)))
    df['Number of Heteroatoms'] = df['ligand_smiles'].apply(
        lambda x: Lipinski.NumHeteroatoms(Chem.MolFromSmiles(x)))
    df['SlogP_VSA2'] = df['ligand_smiles'].apply(lambda x: MolSurf.SlogP_VSA2(Chem.MolFromSmiles(x)))
    df['TPSA'] = df['ligand_smiles'].apply(lambda x: MolSurf.TPSA(Chem.MolFromSmiles(x)))

    salt_acid_ratio = model_salt_acid.predict(
        df[[x for x in df.columns if x not in ["metal", "ligand", "ligand_smiles"]]])
    df["salt_acid_ratio"] = salt_acid_ratio

    Vsolv_salt_ratio = model_solv_salt.predict(
        df[[x for x in df.columns if x not in ["metal", "ligand", "ligand_smiles", "salt_acid_ratio"]]])
    df["Vsolv_salt_ratio"] = Vsolv_salt_ratio

    Tsynth = model_temp_synth.predict(
        df[[x for x in df.columns if x not in ["metal", "ligand", "ligand_smiles",
                                               "salt_acid_ratio", "Vsolv_salt_ratio"]]])
    df["Tsynth"] = Tsynth

    # all necessary properties for predicting the synthesis
    df_params = df[['Regeneration temperature of the sample, °C',
                    'Specific volume of micropores, cm3/g',
                    'Standard characteristic energy of benzene adsorption, kJ/mol',
                    'Mean effective half-width of micropores, nm',
                    'Ultimate adsorption value of nitrogen in micropores, mmol/g',
                    'Characteristic energy of nitrogen adsorption, kJ/mol',
                    'Specific surface area, m2/g', 'Total pore volume, cm3/g',
                    'Mesopore surface area, m2/g', 'Mesopore volume, cm3/g',
                    'Total molecular weight (metal)', 'Average ionic radius (metal)',
                    'Average electronegativity (metal)',
                    'Number of Hydrogen Bond Donors', 'Number of Hydrogen Bond Acceptors',
                    'The exact molecular weight of the molecule, g/mol',
                    'Number of Heteroatoms', 'SlogP_VSA2', 'TPSA',
                    ]]

    df_params.columns = [
        "Температура регенерации образца, °C",
        "Удельный объем микропор, cm3/g",
        "Стандартная энергия адсорбции бензола, kJ/mol",
        "Средняя полуширина микропор, nm",
        "Предельная адсорбция азота в микропорах, mmol/g",
        "Характеристическая энергия адсорбции азота, kJ/mol",
        "Удельная площадь поверхности, m2/g",
        "Суммарный объем пор, cm3/g",
        "Удельная поверхность мезопор, m2/g",
        "Объем мезопор, cm3/g",
        "Общий молекулярный вес (металл)",
        "Средний ионный радиус (металл)",
        "Средняя электроотрицательность (металл)",
        "Количество донорных водородных связей",
        "Количество акцепторных водородных связей",
        "Точный молекулярный вес молекулы, g/mol",
        "Количество гетероатомов",
        "SlogP_VSA2",
        "TPSA"]

    return df_params, df[["metal", "ligand", "salt_acid_ratio", "Vsolv_salt_ratio", "Tsynth"]]
