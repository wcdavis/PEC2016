import sys, csv


def cull_partisan_approvals(input_csv, output_csv):
    outrows = [];
    with open(input_csv, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            if not [s for s in ['independent', 'republican', 'democrat', 'gop'] if s in row[5].lower()]:
                outrows.append(row)

    with open(output_csv, 'w') as out_file:
        csvwriter = csv.writer(out_file)
        csvwriter.writerows(outrows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Usage: requires 2 arguments: input_csv output_csv")
    cull_partisan_approvals(sys.argv[1], sys.argv[2])