#! python3

# Kyle Crosby, Theory of Computing Project 2

import csv
import sys

# Breadth-first search through NTM configurations
def ntm_bfs(ntm, tape, depth_limit):
    # Initial configuration
    configs = [[["", ntm['start'], tape]]]
    # Track spot in tree we're writing to
    level = 0
    index = 0
    end = False
    end_type = ''
    while not end:
        curr = configs[level][index]

        # End search if reached accept state
        if curr[1] == ntm['accept']: 
            end_type = 'accepted'
            break
        
        # Add new level if done with previous
        if len(configs) == level + 1:
            configs.append([])

        # Add new configurations to next level based on dictionary options for current state and input
        if curr[1] != ntm['reject']:
            transition_made = False
            # Loop through all transitions available from current state
            for next in ntm[curr[1]]:
                # Check if input symbol matches next on tape. 
                if next[0] == curr[2][0]:
                    transition_made = True
                    # Move head right
                    if next[3] == 'R':
                        if curr[2][1:] == "":
                            # Adds blank when at end of line
                            configs[level+1].append([curr[0]+next[2], next[1], '_'])
                        else:
                            configs[level+1].append([curr[0]+next[2], next[1], curr[2][1:]])
                    # Move head left
                    elif next[3] == 'L':
                        if curr[2][1:] == "":
                            # Doesn't add to end if already at end of tape
                            configs[level+1].append([curr[0][:-1], next[1], curr[0][-1]+next[2]])
                        else:
                            configs[level+1].append([curr[0][:-1], next[1], curr[0][-1]+next[2]+curr[2][1:]])
           
            # Rejects if no transitions made with current input
            if not transition_made:
                configs[level+1].append([curr[0], ntm['reject'], curr[2]])
        
        # Increment spot in current level
        index += 1
        # Check if should move to next level and reject conditions
        if index > len(configs[level]) - 1:
            end = True
            end_type = 'rejected'
            # End if all rejects
            for c in configs[level]:
                if c[1] != ntm['reject']: 
                    end = False
                    end_type = ''
                    break
            # End if tree is done
            if configs[level+1] == []: 
                end = True
            level += 1
            index = 0
            # End if depth limit reached
            if level > depth_limit:
                end_type = 'limit'
                end = True
            
    return configs, end_type


def simulate_ntm(tape, file_name, depth_limit):
    # Build dictionary of NTM from CSV file
    ntm = {}
    with open(f'test_files/{file_name}', mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.reader(file)
        for i, v in enumerate(csv_reader):
            if i < 7:
                if i == 0:
                    ntm['Name'] = v[0]
                elif i == 1:
                    ntm['Q'] = v
                elif i == 2:
                    ntm['Σ'] = v
                elif i == 3:
                    ntm['Γ'] = v
                elif i == 4:
                    ntm['start'] = v[0]
                elif i == 5:
                    ntm['accept'] = v[0]
                elif i == 6:
                    ntm['reject'] = v[0]
            else:
                if v[0] not in ntm: ntm[v[0]] = []
                ntm[v[0]].append(v[1:])
        
    # Run bfs on the NTM description
    configs, end_type = ntm_bfs(ntm, tape, depth_limit)
                
    return configs, ntm, end_type


def output(configs, ntm, tape, end_type):
    # Print output
    print(f"Machine Name: {ntm['Name']}")
    print(f"Initial String: {tape}")
    print(f"Tree Depth: {len(configs)-1}")
    print(f"Total Transitions Simulated: {sum([len(x) for x in configs])}")
    print(f"Measured nondeterminism: {sum([len(x) for x in configs if x != []]) / (len([x for x in configs if x != []]))}")
    if end_type == 'accepted':
        print(f"String accepted in {len(configs)-1}")
        for level in configs:
            p = ''
            for c in level:
                p += ''.join(c) + ' '
            print(p)
    elif end_type == 'rejected':
        print(f"String rejected in {len(configs)-1}")
    elif end_type == 'limit':
        print(f"Execution stopped after {len(configs)}")


def main():
    # Input format: tape_string depth_limit file_name
    # e.g. (aaa 50 sample_ntm_2_a_plus.csv)
    for line in sys.stdin:
        configs, ntm, end_type = simulate_ntm(line.strip().split()[0], line.strip().split()[2], int(line.strip().split()[1]))
        output(configs, ntm, line.strip().split()[0], end_type)
        print("")



if __name__ == '__main__':
    main()