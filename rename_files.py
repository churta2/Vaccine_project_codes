import os
# Function to rename multiple files
def main():
   i = 0
   path="C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_Project/sf_new_march_data_WA/data_0.2_0.2_future/"
   for filename in os.listdir(path):
      my_dest ="Graph_" + str(i) + ".pkl"
      my_source =path + filename
      my_dest =path + my_dest
      # rename() function will
      # rename all the files
      os.rename(my_source, my_dest)
      i += 1
# Driver Code
if __name__ == '__main__':
   # Calling main() function
   main()