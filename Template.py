import sys
import tkinter
import tkinter.messagebox

import numpy as np
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd


def create_query(features):
    """Create a Prolog query based on the extracted features."""
    # Assuming features are in the same order as DataFrame columns
    columns = ['Destinations', 'country', 'region', 'Climate', 'Budget', 'Activity', 'Demographics', 'Duration',
               'Cuisine', 'History', 'Natural Wonder', 'Accommodation', 'Language']

    # Start building the query
    query = "destination("

    # Add each feature to the query
    for i in range(len(columns)):
        if i < len(features):
            # If there is a feature for this column, add it to the query
            query += f"\'{features[i]}\', "
        else:
            # If there is no feature for this column, use a variable
            query += f"{columns[i]}, "

    # Remove trailing comma and space, add closing parenthesis
    query = query[:-2] + ")"

    return query


class App(tkinter.Tk):
    APP_NAME = "map_view_demo.py"
    WIDTH = 800
    HEIGHT = 750  # This is now the initial size, not fixed.

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area and submit button combined row
        self.grid_rowconfigure(1, weight=4)  # Map row

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self, height=5)  # Reduced height for text area
        self.text_area.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=0, column=0, pady=(0, 10), padx=10,
                                sticky="se")  # Placed within the same cell as text area

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers
        self.marker_path = None

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area can expand/contract.
        self.grid_rowconfigure(1, weight=0)  # Submit button row; doesn't need to expand.
        self.grid_rowconfigure(2, weight=3)  # Map gets the most space.

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self)
        self.text_area.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=1, column=0, pady=10, sticky="ew")

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=2, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers

    def check_connections(self, results):
        print('result2 ', results)
        locations = []
        for result in results:
            city = result["City"]
            locations.append(city)
            # TODO 5: create the knowledgebase of the city and its connected destinations using Adjacency_matrix.csv

        return locations

    def process_text(self):
        """Extract locations from the text area and mark them on the map."""
        text = self.text_area.get("1.0", "end-1c")  # Get text from text area
        locations = self.extract_locations(text)  # Extract locations (you may use a more complex method here)

        # TODO 4: create the query based on the extracted features of user desciption
        ################################################################################################
        query = create_query(locations)
        results = list(prolog.query(query))
        print(results)
        locations = self.check_connections(results)
        # TODO 6: if the number of destinations is less than 6 mark and connect them 
        ################################################################################################
        print(locations)
        locations = ['mexico_city', 'rome', 'brasilia']
        self.mark_locations(locations)

    def mark_locations(self, locations):
        """Mark extracted locations on the map."""
        for address in locations:
            marker = self.map_widget.set_address(address, marker=True)
            if marker:
                self.marker_list.append(marker)
        self.connect_marker()
        self.map_widget.set_zoom(1)  # Adjust as necessary, 1 is usually the most zoomed out

    def connect_marker(self):
        print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if hasattr(self, 'marker_path') and self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def extract_locations(self, text):
        # TODO 3: extract key features from user's description of destinations
        ################################################################################################

        # Convert the text to lowercase and split it into words
        text = text.lower()
        # Define the separators
        separators = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", "=",
                      "~", "`", "{", "}", "[", "]", ";", ":", "'", "\"", "/", ".", ",",
                      " ", "\t", "\n"]
        # Start with the original text
        split_text = [text]
        # Apply the split method for each separator
        for sep in separators:
            split_text = [substr.split(sep) for substr in split_text]
            split_text = [item for sublist in split_text for item in sublist]

        # Convert the list of words into a numpy array
        words_array = np.array(split_text)
        # Create a list to store the important words found in the text
        important_words_found = []
        # Iterate over each important word
        for word in unique_attributes:
            # Use numpy's 'in1d' function to check if the important word is in the words array
            if np.in1d(word, words_array):
                important_words_found.append(word)

        # Convert the list of important words found into a numpy array
        important_words_array = np.array(important_words_found)

        return important_words_array

    def start(self):
        self.mainloop()


# TODO 1: read destinations' descriptions from Destinations.csv and add them to the prolog knowledge base
################################################################################################
# STEP1: Define the knowledge base of cities and their attributes
prolog = Prolog()
df = pd.read_csv('Destinations.csv')
df_size = df.shape[0]  # Use number of rows
prolog.retractall("destination(_, _, _, _, _, _, _, _, _, _, _, _, _)")

for i in range(df_size):
    fact = f"destination(\"{df['Destinations'][i]}\", \'{df['country'][i]}\', \'{df['region'][i]}\', \'{df['Climate'][i]}\', \'{df['Budget'][i]}\', " \
           f" \'{df['Activity'][i]}\', \'{df['Demographics'][i]}\', \'{df['Duration'][i]}\', \'{df['Cuisine'][i]}\', \'{df['History'][i]}\', \'{df['Natural Wonder'][i]}\', " \
           f" \'{df['Accommodation'][i]}\', \'{df['Language'][i]}\')"
    prolog.assertz(fact)


# TODO 2: extract unique features from the Destinations.csv and save them in a dictionary
################################################################################################
unique_attributes = df['country'].unique()
unique_attributes = np.concatenate([unique_attributes, df['region'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Climate'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Budget'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Activity'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Demographics'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Duration'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Cuisine'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['History'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Natural Wonder'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Accommodation'].unique()])
unique_attributes = np.concatenate([unique_attributes, df['Language'].unique()])
unique_attributes = np.array(unique_attributes, dtype=str)
unique_attributes = np.char.lower(unique_attributes)


if __name__ == "__main__":
    app = App()
    app.start()
