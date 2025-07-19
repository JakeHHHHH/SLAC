import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as pw
import numpy
import os



class AJA_df(pd.DataFrame):

    #Variables Used at the SLAC AJA Sputterer

    variables = [
        "Date", "Time", "Layer #", "Sub. Rot.", "Sub. Rot. Speed", "Sub. Z Height", "C.M. Press.", "VAT Press Mode",
        "VAT Pos STPT", "VAT Pos Mode", "Gas#1 Flow", "Gas#1 STPT", "Gas#2 Flow", "Gas#2 STPT", "Gas#3 Flow",
        "Gas#3 STPT", "Sub. Temp.", "Sub. Temp. STPT", "RF#1 W Fbdk", "RF#1 DC Bias", "RF#1 Plasma", "RF#1 Shutter",
        "RF#1 TGT", "RF#1 KWH", "RF#1 STPT", "RF#2 W Fbdk", "RF#2 DC Bias", "RF#2 Plasma", "RF#2 Shutter",
        "RF#2 TGT", "RF#2 KWH", "RF#2 STPT", "RF#3 W Fbdk", "RF#3 DC Bias", "RF#3 Plasma", "RF#3 Shutter",
        "RF#3 TGT", "RF#3 KWH", "RF#3 STPT", "DC#1 W Fdbk", "DC#1 V Fdbk", "DC#1 mA Fdbk", "DC#1 Plasma",
        "DC#1 Shutter", "DC#1 TGT", "DC#1 KWH", "DC#1 STPT", "DC#1 MODE", "DC#2 W Fdbk", "DC#2 V Fdbk",
        "DC#2 mA Fdbk", "DC#2 Plasma", "DC#2 Shutter", "DC#2 TGT", "DC#2 KWH", "DC#2 STPT", "DC#2 MODE",
        "DC#3 W Fdbk", "DC#3 V Fdbk", "DC#3 mA Fdbk", "DC#3 Plasma", "DC#3 Shutter", "DC#3 TGT", "DC#3 KWH",
        "DC#3 STPT", "DC#3 MODE", "DC SWITCH POS", "DC#5 W Fdbk", "DC#5 V Fdbk", "DC#5 mA Fdbk", "DC#5 Plasma",
        "DC#5 Shutter", "DC#5 TGT", "DC#5 KWH", "DC#5 STPT", "DC#5 MODE"
    ]

    # Change at disgression
    plasma_dict = {
        "RF#1 Shutter": "AL",
        "RF#2 Shutter": "Hf",
        "DC#1 Shutter": "Ti",
        "DC#2 Shutter": "Nb",
        "DC#3 Shutter": "Sn",
        "DC#5 Shutter": "Ta"
    }



    def __init__(self, file_path, /, color_palette = []):
        self.path = file_path
        self.target_folder, self.sample_name = "\\".join(file_path.split("\\")[:-1]), file_path.split("\\")[-1].split(".")[0]
        self.df = pd.read_csv(file_path, skiprows=1)
        if color_palette:
            color_palette = ['dodgerblue','mediumseagreen','goldenrod','indianred','slateblue','tomato','orchi+d','darkcyan',
                             'rosybrown','steelblue','coral','darkorange','limegreen',
                            'sienna','mediumvioletred','peru','teal','cadetblue','palevioletred','darkkhaki']
        self.color_palette = color_palette
        self.time_increment = self.get_time_increment()



    def set_color_palette(self, color_palette: list):
        self.color_palette = color_palette
    def get_layer_num(self) -> int:
        return int(self.df['Layer #'].iloc[-1])

    def get_random_color_list(self) -> list:
        return [i for i in self.color_palette[0:self.get_layer_num()]]

    def get_layer_names(self) -> list:

        sample_number = self.sample_name.split("_")[1] 

        file_list = [f for f in os.listdir(self.target_folder) if (os.path.isfile(os.path.join(self.target_folder, f)) and f[-3:] == "ajp")]
        name = [f for f in file_list if f.count(sample_number) == 1][0]
        line = ""
        with open(self.target_folder + "\\" + name, "r") as f:
            line = f.readline()
        my_list =line.split("\x00")
        my_list = [i.split("_", 1)[1] for i in my_list if len(i) > 3]

        return my_list

    def get_layer_range(self) -> list:
        layer_ranges = []
        current_layer = 1
        start = 0
        end = 0
        for i in range(len(self.df['Time'])):
            if self.df["Layer #"][i] > current_layer:
                layer_ranges.append((start, end))
                #layer_ranges.append((df['Time'][start],df['Time'][end]))
                start = i
                end = start
                current_layer += 1
            elif i == len(self.df['Time']) -1:
                layer_ranges.append((start, end))
            else:
                end += 1 
        return layer_ranges


    def get_time_increment(self):

        date_time_column = pd.to_datetime(self.df['Time'], format='%I:%M:%S %p')
        delta = date_time_column.iloc[1] - date_time_column.iloc[0]
        

        return delta.total_seconds()
    

    def get_plasma_times(self) -> list:
        """
        Returns a tuple of conting the name of the plasama and how long it was on for
        with an uncertainty determine by the tume increment
        """

        layer_ranges = self.get_layer_range()
        layer_names = self.get_layer_names()
        plasma_layers_tuple = [(layer_names[i],layer_ranges[i]) for i in range(len(layer_names)) if layer_names[i].contains("nm")]
        shutter_columns = [self.df[i] for i in self.variables if "Shutter" in  i]

        plasma_times = []
        for plasma_layer in plasma_layers_tuple[1]:
            time_interval = 0
            for column in shutter_columns:
                for i in column[layer_ranges]:
                    if i == "ON":
                        time_interval += 1
            plasma_times.append( AJA_df.plasma_dict[plasma_layer], time_interval * self.get_time_increment())
        return plasma_times
    
    def get_relative_time_column(self):
        """
        Returns a column of relative time in seconds
        """
        date_time_column = pd.to_datetime(self.df['Time'], format='%I:%M:%S %p')
        relative_time = (date_time_column - date_time_column.iloc[0]).dt.total_seconds()
        return relative_time
    

class AJA_plot():
    preset = {
        "None" : None,
        "Temp vs. Time" : None,
        "Temp vs. Time with Layers": None,
        "Temp & STPT vs. Time": None,
        "Temp & STPT vs. Time with Layers": None,
        "Pressure vs. Time": None,
        "Pressure vs. Time with Layers": None,
        "Material vs. Time": None,
        "Material vs. Time with Layers":None,
    }

    def __init__(self, aja_df: AJA_df, preset = "None"):
        pass



if __name__ == "__main__":
    df = AJA_df(r"sample_folder\datalogs\20250714_XRR04_S055_30C_3nm Ta_600C_97_nm_Ta_TaOx_14-Jul-25_ 4_55_14 PM.csv")
    print(df.get_layer_num())
    #print(df.get_layer_names())
    #print(df.get_layer_range())
    print(df.get_time_increment())
    print(df.get_plasma_times())
    print(df.get_plasma_range())