import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd


def lower_case_df(dataframe: pd.DataFrame):
    """Lower-case all cell values in a pandas dataframe."""
    for col in dataframe.columns:
        if pd.api.types.is_string_dtype(dataframe[col]):
            dataframe[col] = dataframe[col].str.lower()

    dataframe.columns = dataframe.columns.str.lower()

    return dataframe

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

        # In your GUI initialization code, link this function to a button
        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.pack()

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
        AdjMatrixDf = pd.read_csv("Adjacency_matrix.csv")

        AdjMatrixDf = lower_case_df(AdjMatrixDf.copy())

        # Clear any previous Prolog knowledge base
        prolog.retractall("connected(_, _)")
        prolog.retractall("path(_, _)")  # Also clear any existing path rules

        # Assert Prolog rules for direct and indirect connections
        prolog.assertz("path(X, Y) :- connected(X, Y)")  # Direct connection
        prolog.assertz("path(X, Y) :- connected(X, Z), path(Z, Y)")  # Indirect connection (recursive)

        for j in range(AdjMatrixDf.shape[0]):
            for k in range(AdjMatrixDf.shape[1]):
                if AdjMatrixDf.iloc[j, k] == 1:
                    CityJ = AdjMatrixDf.iloc[0,j]
                    CityK = AdjMatrixDf.iloc[k - 1,0]
                    query = f"connected(\"{CityJ}\", \"{CityK}\")"
                    prolog.assertz(query)

        # Extract city names and create Prolog facts for connected cities
        for result in results:
            city = result["City"]
            locations.append(city)

        connected_cities = []
        # Query for paths between cities
        if locations.__sizeof__() > 1:
            for start_city in locations:
                for end_city in locations:
                    query = "path({}, {})".format(start_city, end_city)
                    answer = prolog.query(query)
                    if start_city != end_city and answer:
                        print("Path found between {} and {}".format(start_city, end_city))
                        connected_cities.append(start_city)
                        connected_cities.append(end_city)

                    else:
                        print("No path found between {} and {}".format(start_city, end_city))

        return locations

    def process_text(self):
        # Extract locations from the user's input
        text = self.text_area.get("1.0", 'end-1c')
        locations = self.extract_locations(text)  # Extract locations (you may use a more complex method here)

        # TODO 4: create the query based on the extracted features of user description
        ################################################################################################
        # Initialize an empty list to store the values
        values_list = []
        for values in locations.values():
            if values:
                values_list.append(f"'{values[0]}'")
            else:
                values_list.append("_")

        values_str = ", ".join(values_list)
        query_str = f"destination(City, {values_str})"
        results = list(prolog.query(query_str))
        print(results)

        locations = self.check_connections(results)
        # TODO 6: if the number of destinations is less than 6 mark and connect them
        ################################################################################################
        if len(results) > 5:
            tkinter.messagebox.showinfo("Too many destinations", "Information is not enough for specific destinations")
            self.text_area.delete('1.0', tkinter.END)
        else:
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

        two_word_combinations = [" ".join(pair) for pair in zip(split_text, split_text[1:])]

        # Create a dictionary to store the important words found in the text
        important_words_found = {'country': [], 'region': [], 'climate': [],
                                 'budget': [], 'activity': [], 'demographics': [],
                                 'duration': [], 'cuisine': [], 'history': [],
                                 'natural wonder': [], 'accommodation': [], 'language': []}

        # Iterate over each text word
        for word in split_text:
            for key in unique_attributes:
                for value in unique_attributes[key]:
                    if word == value:
                        important_words_found[key].append(word)
        for word in two_word_combinations:
            for key in unique_attributes:
                for value in unique_attributes[key]:
                    if word == value:
                        important_words_found[key].append(word)

        return important_words_found

    def start(self):
        self.mainloop()


# TODO 1: read destinations' descriptions from Destinations.csv and add them to the prolog knowledge base
################################################################################################
prolog = Prolog()
df = pd.read_csv('Destinations.csv')
df = df.apply(lambda s: s.str.lower() if s.dtype == 'object' else s)
df_size = df.shape[0]  # Use number of rows
prolog.retractall("destination(_, _, _, _, _, _, _, _, _, _, _, _, _)")

for i in range(df_size):
    fact = f"destination(\"{df['Destinations'][i]}\", \'{df['country'][i]}\', \'{df['region'][i]}\', " \
           f" \'{df['Climate'][i]}\', \'{df['Budget'][i]}\', \'{df['Activity'][i]}\', \'{df['Demographics'][i]}\', " \
           f" \'{df['Duration'][i]}\', \'{df['Cuisine'][i]}\', \'{df['History'][i]}\', \'{df['Natural Wonder'][i]}\', " \
           f" \'{df['Accommodation'][i]}\', \'{df['Language'][i]}\')"
    prolog.assertz(fact)

# TODO 2: extract unique features from the Destinations.csv and save them in a dictionary
################################################################################################
unique_attributes = {'country': [item.lower() for item in df['country'].unique().tolist()],
                     'region': [item.lower() for item in df['region'].unique().tolist()],
                     'climate': [item.lower() for item in df['Climate'].unique().tolist()],
                     'budget': [item.lower() for item in df['Budget'].unique().tolist()],
                     'activity': [item.lower() for item in df['Activity'].unique().tolist()],
                     'demographics': [item.lower() for item in df['Demographics'].unique().tolist()],
                     'duration': [item.lower() for item in df['Duration'].unique().tolist()],
                     'cuisine': [item.lower() for item in df['Cuisine'].unique().tolist()],
                     'history': [item.lower() for item in df['History'].unique().tolist()],
                     'natural wonder': [item.lower() for item in df['Natural Wonder'].unique().tolist()],
                     'accommodation': [item.lower() for item in df['Accommodation'].unique().tolist()],
                     'language': [item.lower() for item in df['Language'].unique().tolist()]}

if __name__ == "__main__":
    app = App()
    app.start()
