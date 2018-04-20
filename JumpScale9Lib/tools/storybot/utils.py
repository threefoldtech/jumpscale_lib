from js9 import j

logger = j.logger.get("j.tools.StoryBot")

def _parse_body(body, item):
    """Parses story or task item into the provided body
    
    Arguments:
        body str -- body in which to add the item
        item Task or Story -- item to add to the body (type Task or Story)
    
    Returns:
        str -- Updated body
    """

    start_list, end_list = _get_indexes_list(body, title=item.LIST_TITLE)
    if start_list == -1:
        logger.debug("list not found, adding one")
        if not body.endswith("\n\n") and not body.endswith("\r\n"):
            body += "\n"
        body +="\n## %s\n\n%s" % (item.LIST_TITLE, item.md_item)

    elif end_list == -1:
        item_i = item.index_in_body(body, start_i=start_list, end_i=end_list)
        if item_i != -1 :
            logger.debug("Item already in list at index %s" % str(item_i))
            body = _update_done_item(body,item_i, item.done_char)
        else:
            if not body.endswith("\n"):
                body += "\n"

            body += item.md_item

    else:
        item_i = item.index_in_body(body, start_i=start_list, end_i=end_list)
        if item_i != -1 :
            logger.debug("Item already in list")
            body = _update_done_item(body, item_i, item.done_char)
        else:
            # squeeze in task at the end of list
            lines = body.splitlines()
            lines.insert(end_list + 1, item.md_item)
            body = "\n".join(lines)

    return body

def _get_indexes_list(body, title="Stories"):
    """Get the start and end index of the storylist in a body
    Start index is -1 if not list is found
    If start index is not -1 and end index is -1,  the last line of the body is the last item of the list
    
    Arguments:
        body str -- body of the task issue where we should check the story list
    
    Returns:
        int -- start index
        int -- end index
    """
    start_index = -1
    end_index = -1

    title_line = -1
    lines = body.splitlines()
    for i, line in enumerate(lines):
        # check for list title
        if line.startswith("## %s" % title):
            title_line = i
            continue

        if title_line != -1:
            continue
        
        # find start of list
        if line.strip() == "" and start_index == -1:
            continue

        # find end of list (empty line after list item)
        elif line.strip() == "" and start_index != -1:
            end_index = i - 1
            break

        elif line.startswith("- [") and start_index == -1:
            start_index = i

        elif start_index != -1 and (not line.startswith("- [") or line.strip() == ""):
            raise RuntimeError("Story list is wrongfully formatted")

    if title_line != -1 and start_index == -1:
        start_index = title_line
    return start_index, end_index

def _update_done_item(body, index, done_char):
    """Checks if done character at body line index (that should be a task/story list item) corresponds to the one provided.
    Update char if not so.
    
    Arguments:
        body str -- Issue body
        index int -- line index of list item
        done_char str -- Tick character to make item done or not (should be: "x", " ", or "")
    
    Returns:
        string -- Updated body
    """
    lines = body.splitlines()
    line = lines[index]
    start = line.find("[") + 1
    end = line.find("]")
    cur_tick = line[start:end]

    if cur_tick != done_char:
        # update line
        logger.debug("Updating item at line: %s" % index)
        line = line[:start] + done_char + line[end:]
        lines[index] = line
        body = "\n".join(lines)

    return body

def _index_story(stories, title):
    """Returns index of title in story list
    returns -1 if not found
    
    Arguments:
        stories [Story] -- List of stories (Story)
        title str -- Story title to look for in list
    """
    for i, story in enumerate(stories):
        if story == title:
            return i
    return -1

def _repoowner_reponame(repo_str, username):
    """Returns a repo owner and repo name from a repo string (owner username(or org)/repo name)
    If only repo is given, username will be provided username who's using the API
    
    Arguments:
        repo_str str -- Full repo string (owner username(or org)/repo name)
        username str -- Username of current user
    
    Raises:
        ValueError -- Invalid repo_str
    """

    user = ""
    repo = ""
    split = repo_str.split("/")
    if len(split) == 1:
        user = username
        repo = split[0]
    elif len(split) == 2:
        user = split[0]
        repo = split[1]
    else:
        raise ValueError("Repo %s is made of %s parts, only 1 and 2 part repo names are supported" % (repo, str(len(repo))))

    return user, repo

def _find_second(str, char="["):
    """Returns index of second occurrence of char in line
    
    Arguments:
        str str -- string to look in (default: "[")

    Keyword Arguments:
        char str -- char to look the second occurrence of

    Returns:
        int -- index of second occurrence
    """
    start = str.find(char)
    return str.find(char, start +1) + 1
