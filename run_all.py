import data_parser as parse
import calculate_elos as calc
import predict_next_event as predict
from datetime import datetime

print('Running Parser')
parse.main()

print('Calculating new elos')
calc.main()

print('Predicting Next Event')
predict.main()

with open("log.txt", "a") as log_file:
    log_file.write(f"{datetime.now()}\n")
