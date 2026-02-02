def get_metadata(header):
    # header = df.columns.tolist()
    
    # get metadata part
    # for i,s in enumerate(header):
    #     if 'metadata=[' in s:
    #         header = header[i:]
    #         break
    # header = ','.join(header)
    # connect embeded arrays
    # parse metadata
    s_metadata = header
    s_metadata = s_metadata.split("metadata=[")[1]
    s_metadata = s_metadata[:-2]
    # s_metadata = s_metadata[s_metadata.index("metadata=[")+1 : s_metadata.index("]")]
    # split into key=value pairs
    # s_metadata = s_metadata.split(",")

    # build dictionary
    metadata = {}
    while s_metadata:
        # skip leading commas/spaces
        s_metadata = s_metadata.lstrip(', ')
        if not s_metadata:
            break

        # split key
        eq_idx = s_metadata.find('=')
        if eq_idx == -1:
            break
        key = s_metadata[:eq_idx].strip()
        s_metadata = s_metadata[eq_idx+1:]

        # parse value
        if s_metadata.startswith('['):
            depth = 0
            end_idx = None
            for i, ch in enumerate(s_metadata):
                if ch == '[':
                    depth += 1
                elif ch == ']':
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            if end_idx is None:
                # no matching closing bracket; take entire remainder
                value = s_metadata
                s_metadata = ''
            else:
                value = s_metadata[1:end_idx]
                s_metadata = s_metadata[end_idx+1:]
        else:
            # non-bracket value up to next comma
            comma_idx = s_metadata.find(',')
            if comma_idx == -1:
                value = s_metadata
                s_metadata = ''
            else:
                value = s_metadata[:comma_idx]
                s_metadata = s_metadata[comma_idx+1:]

        metadata[key] = value
    return metadata