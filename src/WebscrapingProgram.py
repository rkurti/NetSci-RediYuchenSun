from TransferDataScraperAndProcessor import *
import time

# Revisions made by Sun Gyu and Redi. 

def main():
    start = time.time()
    scraper_tool = TransferDataScraperAndProcessor(start_year=2000, end_year=2018)
    scraper_tool.write_out_all_clubs_and_leagues()
    scraper_tool.write_out_clubs_and_countries()
    
    # Creates the csv files for number of players transferred for each position.
    scraper_tool.write_output_file_for_pos("")
    scraper_tool.write_output_file_for_pos("front")
    scraper_tool.write_output_file_for_pos("back")
    scraper_tool.write_output_file_for_pos("midfield")
    scraper_tool.write_output_file_for_pos("goalkeeper")
    
    # Creates csv files with normalized amount of money spent for each position.
    scraper_tool.write_output_file_with_weights("")
    scraper_tool.write_output_file_with_weights("front")
    scraper_tool.write_output_file_with_weights("back")
    scraper_tool.write_output_file_with_weights("midfield")
    scraper_tool.write_output_file_with_weights("goalkeeper")

    end = time.time()
    print(str(end - start) + " seconds")


if __name__ == "__main__":
    main()

