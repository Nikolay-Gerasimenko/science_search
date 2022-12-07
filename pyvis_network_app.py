import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import json
import networkx as nx
from pyvis.network import Network

st.set_page_config(layout="wide")

# Read dataset (CSV)
# df_interact = pd.read_csv('data/processed_drug_interactions.csv')

# # Set header title
# st.title('Network Graph Visualization of Drug-Drug Interactions')

# # Define list of selection options and sort alphabetically
# drug_list = ['Metformin', 'Glipizide', 'Lisinopril', 'Simvastatin',
#             'Warfarin', 'Aspirin', 'Losartan', 'Ibuprofen']
# drug_list.sort()

# # Implement multiselect dropdown menu for option selection (returns a list)
# selected_drugs = st.multiselect('Select drug(s) to visualize', drug_list)

# # Set info message on initial site load
# if len(selected_drugs) == 0:
#     st.text('Choose at least 1 drug to start')

# # Create network graph when user selects >= 1 item
# else:
#     df_select = df_interact.loc[df_interact['drug_1_name'].isin(selected_drugs) | \
#                                 df_interact['drug_2_name'].isin(selected_drugs)]
#     df_select = df_select.reset_index(drop=True)

#     # Create networkx graph object from pandas dataframe
#     G = nx.from_pandas_edgelist(df_select, 'drug_1_name', 'drug_2_name', 'weight')

#     # Initiate PyVis network object
#     drug_net = Network(
#                        height='400px',
#                        width='100%',
#                        bgcolor='#222222',
#                        font_color='white'
#                       )

#     # Take Networkx graph and translate it to a PyVis graph format
#     drug_net.from_nx(G)

#     # Generate network with specific layout settings
#     drug_net.repulsion(
#                         node_distance=420,
#                         central_gravity=0.33,
#                         spring_length=110,
#                         spring_strength=0.10,
#                         damping=0.95
#                        )

#     # Save and read graph as HTML file (on Streamlit Sharing)
#     try:
#         path = '/tmp'
#         drug_net.save_graph(f'{path}/pyvis_graph.html')
#         HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

#     # Save and read graph as HTML file (locally)
#     except:
#         path = '/html_files'
#         drug_net.save_graph(f'{path}/pyvis_graph.html')
#         HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# #     Load HTML file in HTML component for display on Streamlit page
#     components.html(HtmlFile.read(), height=435)

# # Footer
# st.markdown(
#     """
#     <br>
#     <h6><a href="https://github.com/kennethleungty/Pyvis-Network-Graph-Streamlit" target="_blank">GitHub Repo</a></h6>
#     <h6><a href="https://kennethleungty.medium.com" target="_blank">Medium article</a></h6>
#     <h6>Disclaimer: This app is NOT intended to provide any form of medical advice or recommendations. Please consult your doctor or pharmacist for professional advice relating to any drug therapy.</h6>
#     """, unsafe_allow_html=True
#     )

##############################################################################################################################
fos_df = pd.read_csv('data/fos_df.csv')
fos_df.dropna(inplace=True)
children_fos_df1 = pd.read_csv('data/children_fos_df_part1.csv')
children_fos_df2 = pd.read_csv('data/children_fos_df_part2.csv')
children_fos_df = pd.concat([children_fos_df1, children_fos_df2], ignore_index=True)


if 'all_foses' not in st.session_state:
    st.session_state['all_foses'] = []

if 'selected_foses' not in st.session_state:
    st.session_state['selected_foses'] = []
    
if 'text_input' not in st.session_state:
    st.session_state['text_input'] = ''
    
if 'rerun_idx' not in st.session_state:
    st.session_state['rerun_idx'] = 0


def get_entity_by_name(fos_name):
    return fos_df[fos_df.prep_name == fos_name.lower()].entity.values[0]


def get_parents(entity):
    return children_fos_df[children_fos_df.children_fos == entity].parent_fos.values


def get_children(entity):
    return children_fos_df[children_fos_df.parent_fos == entity].children_fos.values


def get_brothers(entity):
    return [child for parent in get_parents(entity) for child in get_children(parent)]


def get_connection_power(name1, name2):
    entity1 = get_entity_by_name(name1)
    entity2 = get_entity_by_name(name2)
    df1 = children_fos_df[(children_fos_df.parent_fos == entity1) & (children_fos_df.children_fos == entity2)]
    if len(df1):
        return df1.iloc[0].connection_power
    else:
        df2 = children_fos_df[(children_fos_df.parent_fos == entity2) & (children_fos_df.children_fos == entity1)]
        if len(df2):
            return df2.iloc[0].connection_power    
    
    
#     connection_powers = children_fos_df[children_fos_df.parent_fos == request].connection_power.values


st.markdown("<h2 style='text-align: center; color: white;'>Enter your query</h2>", unsafe_allow_html=True)

text_request = set(st.text_input('').lower().split())

if text_request != st.session_state['text_input']:
    st.session_state['text_input'] = text_request
    st.session_state['all_foses'] = []
    st.session_state['selected_foses'] = []

fos_df['match_len'] = fos_df.prep_name.apply(lambda name: len(set(name.split()) & text_request))
foses = fos_df[fos_df['match_len'] > 0].sort_values('match_len', ascending=False).name.values.tolist()

for fos in foses:
    if fos not in st.session_state.all_foses:
        st.session_state.all_foses.append(fos)

max_n = st.selectbox('Choose max N of children and parents of node', list(range(1, 100)))
log_degree = st.selectbox('Choose degree of logarithm', list(range(1, 10)), index=1)
fos_df['log_power'] = fos_df.power.apply(lambda power: math.log(power, log_degree))
power_dict = dict(fos_df[['name', 'log_power']].to_records(index=False))



st.markdown("<h2 style='text-align: center; color: white;'>Choose nodes to go deeper</h2>", unsafe_allow_html=True)
last_selected_foses = st.session_state.selected_foses
selected_foses = st.multiselect('', st.session_state.all_foses,
                                default=st.session_state.selected_foses)
# st.session_state.rerun_idx += 1
# if st.session_state.rerun_idx % 2 == 0:
#     st.experimental_rerun()

for fos in selected_foses:
    if fos not in st.session_state.selected_foses:
        st.session_state.selected_foses.append(fos)

with open('selected_foses.json', 'w') as f:
    json.dump(st.session_state.selected_foses, f)

results = {}
for request in selected_foses:
    result_entities = get_children(get_entity_by_name(request))
    result_df = fos_df.loc[fos_df[fos_df.entity.isin(result_entities)].index].sort_values('rank').iloc[:max_n]
    results[request] = result_df
foses = [name for df in results.values() for name in df.name]

for fos in foses:
    if fos not in st.session_state.all_foses:
        st.session_state.all_foses.append(fos)

G = nx.DiGraph()
# for request in selected_foses:
#     connection_powers = children_fos_df[children_fos_df.parent_fos == request].connection_power.values
#     for i in range(len(results[request])):
#         row = results[request].iloc[i]
        
        
        
#         request_df = children_fos_df[children_fos_df.parent_fos == request]
#         connection_power = request_df[request_df.children_fos == row['name']].iloc[0].connection_power
#         G.add_edge(request, row.name, connection_powers[i])
#     if len(results[request]) == 0:, label=row['connection_power']
#         G.add_edge(request, request)

for request in selected_foses:
    for name in results[request].name:
        G.add_edge(request, name, label=round(get_connection_power(request, name), 2))

results = {}
for request in selected_foses:
    result_entities = get_parents(get_entity_by_name(request))
    result_df = fos_df.loc[fos_df[fos_df.entity.isin(result_entities)].index].sort_values('rank').iloc[:max_n]
    results[request] = result_df
foses = [name for df in results.values() for name in df.name]

for fos in foses:
    if fos not in st.session_state.all_foses:
        st.session_state.all_foses.append(fos)

# for request in selected_foses:
#     for i in range(len(results[request])):
#         row = results[request].iloc[i]
#         request_df = children_fos_df[children_fos_df.parent_fos == request]
#         connection_power = request_df[request_df.children_fos == row.name].iloc[0].connection_power
#         G.add_edge(request, row.name, connection_power)
for request in selected_foses:
    for name in results[request].name:
        G.add_edge(name, request, label=round(get_connection_power(request, name), 2))

nt = Network(
    directed=True,
    height='1020px',
    width='100%',
    bgcolor='#222222',
    font_color='white'
)

nx.set_node_attributes(G, power_dict, 'size')
nt.from_nx(G)
nt.repulsion(node_distance=420, central_gravity=0.1,
             spring_length=110, spring_strength=0.10,
             damping=0.95)

nt.save_graph(f'html_files/pyvis_graph.html')
HtmlFile = open(f'html_files/pyvis_graph.html', 'r', encoding='utf-8')
components.html(HtmlFile.read(), height=1050)

cols = st.columns(11)
with cols[int(len(cols) / 2)]:
    st.button('Go dipper!')

##############################################################################################################################
