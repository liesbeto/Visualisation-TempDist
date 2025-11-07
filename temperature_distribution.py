import copy
import numpy as np
import matplotlib.pyplot as plt

CMAP = plt.cm.viridis

class Grid():
    def __init__(self, subdivisions_ninth, epsilon):
        self.subdivisions = subdivisions_ninth * 9 + 2
        self.grid = np.zeros((self.subdivisions, self.subdivisions))
        self.epsilon = epsilon
        self.heatmaps = []

    def set_conditions(self, T_top, T_bath, T_duct):
        self.grid[0,:] = T_top
        self.grid[-1,:] = T_bath
        self.grid[int((self.subdivisions-2)/3)+1:int((self.subdivisions-2)/3)*2+1,int((self.subdivisions-2)/3)+1:int((self.subdivisions-2)/3)*2+1] = T_duct
        self.grid[:,0] = T_bath
        self.grid[:,-1] = T_bath

        five_ninths = int((self.subdivisions-2)*(5/9))

        linear_increase = np.linspace(T_top,T_bath,five_ninths)
        self.grid[0:five_ninths,0] = linear_increase
        self.grid[0:five_ninths,-1] = linear_increase

        self.heatmaps.append(self.grid)

        self.converging_cells = []
        for row in range(1, self.subdivisions-1):
            for column in range(1, self.subdivisions-1):
                if self.grid[row,column] == 0:
                    self.converging_cells.append((row, column))
                    self.grid[row,column] = 90

    def add_timestep(self):
        biggest_change = 0
        grid_temp = copy.deepcopy(self.grid)
        for r, c in self.converging_cells:
            grid_temp[r,c] = (1/4)*(self.grid[r-1,c]+self.grid[r+1,c]+self.grid[r,c-1]+self.grid[r,c+1])
            if abs(grid_temp[r,c] - self.grid[r,c]) > biggest_change:
                biggest_change = abs(grid_temp[r,c] - self.grid[r,c])

        self.grid = grid_temp

        return biggest_change

    def add_timesteps(self):
        biggest_change = self.add_timestep()
        self.heatmaps.append(self.grid)

        while biggest_change > self.epsilon:
            biggest_change = self.add_timestep()
            self.heatmaps.append(self.grid)

    def plot_heatmaps(self):
        plt.imshow(self.heatmaps[0], cmap=CMAP)
        cb = plt.colorbar()
        cb.set_label(r"Temperature ($^{\text{o}}$)")
        plt.title(r"Temperature Distribution in Rye ($t = 0$)")
        plt.show()
        plt.imshow(self.heatmaps[-1], cmap=CMAP)
        cb = plt.colorbar()
        cb.set_label(r"Temperature ($^{\text{o}}$)")
        plt.title(r"Temperature Distribution in Rye ($t = 157$)")
        plt.show()
    
    def write_to_csvs(self):
        for i in range(len(self.heatmaps)):
            heatmap = self.heatmaps[i][::-1]
            filename = "heatmaps/heatmap_" + f"{i}".zfill(4) + ".csv"
            with open(filename, "w") as file:
                for r in range(len(heatmap)):
                    for c in range(len(heatmap[r])):
                        file.write(f"{r},{c},{heatmap[r,c]}\n")


grid1 = Grid(4, 1/10)
grid1.set_conditions(100, 32, 212)
grid1.add_timesteps()
grid1.plot_heatmaps()
grid1.write_to_csvs()
