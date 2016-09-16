# Author: Ryan Buckley <ryancbuckley@gmail.com>

import csv, datetime, pickle, sys
class PollsterEncoding:
    """Provide a relatively neat interface for keeping a table of
    pollster names and corresponding numeric IDs."""
    def __init__(self, filename):
        self.table_file = filename
        self.pollster_table = read_table(self.table_file)

    def get(self, pollster):
        if pollster not in self.pollster_table:
            # Assign an ID to new pollster and insert into table
            self.add(pollster)
        return self.pollster_table[pollster]

    def add(self, pollster):
        assert(pollster not in self.pollster_table)
        self.pollster_table[pollster] = max([0]+self.pollster_table.values())+1
        self.write_table()

    def write_table(self):
        """Write pollster table to pickle file."""
        with open(self.table_file, 'w') as table_f:
            pickle.dump(self.pollster_table, table_f)

def read_table(filename):
    """Read pickle file and return pollster table"""
    try:
        with open(filename, 'r') as table_f:
            return pickle.load(table_f)
    except IOError:
        print "Warning: could not open pollster table file."
        print "Will proceed by inventing new pollster IDs."
        return {}

def datetime_to_datenum(dt_val):
    """Convert a Python datetime to a MATLAB datenum numeric value"""
    date_from_0 = dt_val + datetime.timedelta(days = 366)
    time_fraction = (dt_val.hour*60*60 + dt_val.minute*60 + dt_val.second
                        + dt_val.microsecond*10e-6 )/(60.0*60.0*24.0)
    return date_from_0.toordinal() + time_fraction

def datestr_to_datenum(date_str):
    """Convert a string to a MATLAB datenum numeric value.
    Acceptable formats are 'yyyy-mm-dd' and 'yyyy-mm-dd hh:mm:ss'"""
    try:
        dt_val =  datetime.datetime.strptime(date_str,'%Y-%m-%d')
    except ValueError:
        try:
            dt_val =  datetime.datetime.strptime(date_str,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            # UPDATE 4/6/16: HuffPost decided to change time formats yet again
            try:
                dt_val = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                print "Problem with date value ", date_str
                raise ValueError
    return datetime_to_datenum(dt_val)

def reformat_huffpost_csv(in_filename, out_filename, pollster_file):
    """Convert a csv with Huffington Post polling data to a MATLAB-compatible format.

    Assume column 1 identifies the pollster, and convert to a numeric pollster ID.
    Columns 2, 3, and 4 are dates and are converted to MATLAB datenum format.
    Columns 5 and 6 are discarded.
    Columns 7-9 are kept, unaltered.
    Columns 10+ are discarded.

    The table which maps pollster names to numeric IDs is written to pollster_file.
    New, MATLAB-compatible csv is written to out_filename.
    """

    pollsters = PollsterEncoding(pollster_file)
    outrows = []
    with open(in_filename,'r') as csvfile:
        #has_header = csv.Sniffer().has_header(csvfile.read(8192))
        # UPDATE 9/2/16: HuffPost added a "Question Text" field and had a newline
        # in a question text string, causing the sniffer to choke
        has_header = True # All HuffPost CSVs seem to have a header
        csvfile.seek(0)  # rewind
        csvreader = csv.reader(csvfile)
        if has_header:
            next(csvreader)  # skip header row

        for row in csvreader:
            # Note: python list indices start at 0
            # These numbers are one off from those in the docstring
            row[0] = pollsters.get( row[0] )
            # HuffPo added entry time in addition to date. we look for just a date
            # Plus, the addition of a date added an erroneous date string
            # UPDATE 1/21/16: HuffPost screwed up their output format (again)
            # now just check if length > 1
            if len(row[3].split()) > 1:
                row[3] = row[3].split()[0]
            row[1:4] = (datestr_to_datenum(date) for date in row[1:4])
            outrows.append( row[0:5] + [int(float(x)) if x else "" for x in row[7:10]] )

    with open(out_filename, 'w') as out_file:
        csvwriter = csv.writer(out_file)
        csvwriter.writerows(outrows)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError("Usage: requires 3 arguments: input_csv output_csv pollster_id_table")
    reformat_huffpost_csv(sys.argv[1], sys.argv[2], sys.argv[3])
