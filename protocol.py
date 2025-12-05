from vcs_core import vcs

def process_client_request(username, raw_data):
    """
    Routes the client's command string to the correct Version Control System function.
    """
    data = raw_data.strip()

    # The client now sends the content as part of the EDIT command (EDIT:content)
    if data.startswith("EDIT:"):
        new_content = data[5:].strip()
        status = vcs.edit(username, new_content)
        return f"{status}\n--- Current Draft ---\n{vcs.get_active_branch(username).current_content}"

    elif data.startswith("UNDO"):
        status = vcs.undo(username)
        draft = vcs.get_active_branch(username).current_content
        return f"{status}\n--- Current Draft ---\n{draft}"

    elif data.startswith("REDO"):
        status = vcs.redo(username)
        draft = vcs.get_active_branch(username).current_content
        return f"{status}\n--- Current Draft ---\n{draft}"

    elif data.startswith("BRANCH:"):
        name = data[7:].strip()
        return vcs.create_branch(username, name)

    elif data.startswith("CHECKOUT:"):
        name = data[9:].strip()
        status = vcs.switch_branch(username, name)
        draft = vcs.get_active_branch(username).current_content
        return f"{status}\n--- Current Draft ---\n{draft}"

    elif data.startswith("MERGE:"):
        source_name = data[6:].strip()
        status = vcs.merge(username, source_name)
        draft = vcs.get_active_branch(username).current_content
        return f"{status}\n--- Current Draft ---\n{draft}"

    elif data.startswith("COMMIT"):
        return vcs.commit(username)

    elif data.startswith("PEEK"):
        draft = vcs.get_active_branch(username).current_content
        return f"--- Your Draft ---\n{draft}"

    elif data.startswith("SHOW"):
        content = vcs.official_repository_content
        # The prefix 'SHOW_CONTENT:\n' is used by the client to trigger the GUI.
        return f"SHOW_CONTENT:\n{content}"

    else:
        return "Unknown or malformed command. Please check syntax."