from asyncio import sleep
from datetime import datetime

from pyrogram import Client, types, utils
from pyrogram.raw import functions
from pyrogram.raw.types import InputPeerEmpty, MessageEmpty, Dialog, InputPeerSelf, InputMessagesFilterEmpty
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

app = Client("_client", no_updates=True)
chunk_size = 100

async def main():
    print(f'[{datetime.now()}] Starting app...')
    await app.start()
    
    try:
        print(f'[{datetime.now()}] Collecting groups...')
        groups = await get_groups()
        
        if len(groups) == 0:
            raise Exception('You don\'t participate any group. Aborting...')
        
        print(f'[{datetime.now()}] Sorting groups by title...')
        groups = sorted(groups, key=lambda x: x['title'], reverse=False)
        sel_groups = []
        
        print('\nDelete all your messages in')
        for i, group in enumerate(groups):
            print(f' {i+1:>3}. #{group["id"]:>14} {group["title"]}')
        print(
            f' {len(groups) + 1:>3}. '
            '(!) DELETE ALL YOUR MESSAGES IN ALL OF THOSE GROUPS (!)\n'
        )
        
        nums_str = input('Insert option numbers (comma separated): ')
        nums = map(lambda s: s.strip(), nums_str.split(','))
        
        for n in nums:
            try:
                n = int(n)
            except ValueError:
                continue

            if 1 <= n <= len(groups) and groups[n - 1] not in sel_groups:
                sel_groups.append(groups[n - 1])
                continue

            if n == len(groups) + 1:
                print('\nTHIS WILL DELETE ALL YOUR MESSSAGES IN ALL GROUPS!')
                answer = input('Please type "I understand" to proceed: ')
                if answer.upper() != 'I UNDERSTAND':
                    print('Better safe than sorry. Aborting...')
                    exit(-1)
                sel_groups = groups
                break
        
        if len(sel_groups) < 1:
            raise Exception('No group was selected. Aborting...')
        
        sel_groups = sorted(sel_groups, key=lambda x: x['title'], reverse=False)
        groups_str = '\n - #'.join(f'{c["id"]:>14} {c["title"]}' for c in sel_groups)
        print(f'\nSelected groups:\n - #{groups_str}\n')
        
        await delete_messages_from_groups(sel_groups)
        
    except Exception as e:
        print(f'\n[{datetime.now()}] An exception occurred:\n - {e}')
    
    print(f'\n[{datetime.now()}] Closing app...')
    await app.stop()

async def delete_messages_from_groups(groups):
    for group in groups:
        peer = await app.resolve_peer(group['id'])
        await delete_messages_from_group(group, peer)

async def delete_messages_from_group(group, peer):
    print(f'[{datetime.now()}] Searching your messages in "{group["title"]}"...')
    
    repeat = False
    message_ids = []
    add_offset = 0
    
    while True:
        q = await search_messages(peer, add_offset)
        for msg in q.messages:
            message_ids.append(msg.id)
        messages_count = len(message_ids)
        if messages_count >= q.count:
            break
        if len(q.messages) == 0:
            print(f'[{datetime.now()}] Some messages is missing from search...')
            repeat = True
            break
        add_offset += chunk_size
    
    print(f'[{datetime.now()}] Found {messages_count} of your messages in "{group["title"]}"')
    if len(message_ids) > 0:
        await delete_messages(group['id'], message_ids)
    if repeat:
        await delete_messages_from_group(group, peer)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

async def delete_messages(chat_id, message_ids):
    print(f'[{datetime.now()}] Deleting {len(message_ids)} messages...')
    for chunk in chunks(message_ids, chunk_size):
        await app.delete_messages(chat_id=chat_id, message_ids=chunk)

async def chunk_delete_messages(chat_id, message_ids):
    try:
        await app.delete_messages(chat_id=chat_id, message_ids=message_ids)
    except FloodWait as e:
        await sleep(e.value)
        await chunk_delete_messages(chat_id=chat_id, message_ids=message_ids)

async def search_messages(peer, add_offset):
    print(f'[{datetime.now()}] Searching messages... OFFSET: {add_offset}')
    try:
        r = await app.invoke(
            functions.messages.Search(
                peer=peer,
                q='',
                filter=InputMessagesFilterEmpty(),
                min_date=0,
                max_date=0,
                offset_id=0,
                add_offset=add_offset,
                limit=chunk_size,
                max_id=0,
                min_id=0,
                hash=0,
                from_id=InputPeerSelf()
            )
        )
    except FloodWait as e:
        print(f'[{datetime.now()}] Flood wait... TIME: {e.value}sec')
        await sleep(e.value)
        r = await search_messages(peer, add_offset)
    return r

async def get_groups(limit: int = 0):
    count = await app.get_dialogs_count()
    groups = []
    
    per_page = chunk_size
    current = 0
    total = limit or (1 << 31) - 1
    limit = min(per_page, total)
    offset_date = 0
    offset_id = 0
    offset_peer = InputPeerEmpty()
    cur_page = 0
    
    while True:
        r = await get_dialogs(cur_page, per_page, count, offset_date, offset_id, offset_peer, limit)
        
        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}
        
        messages = {}
        for message in r.messages:
            if isinstance(message, MessageEmpty):
                continue
            chat_id = utils.get_peer_id(message.peer_id)
            messages[chat_id] = await types.Message._parse(app, message, users, chats)
        
        dialogs = []
        for dialog in r.dialogs:
            if not isinstance(dialog, Dialog):
                continue
            dialogs.append(types.Dialog._parse(app, dialog, messages, users, chats))
        
        if not dialogs:
            break
        
        last = dialogs[-1]
        
        offset_id = last.top_message.id
        offset_date = utils.datetime_to_timestamp(last.top_message.date)
        offset_peer = await app.resolve_peer(last.chat.id)
        
        cur_page += 1
        current += 1
        
        for dialog in dialogs:
            if dialog.chat.id < 0 and dialog.chat.type is not ChatType.CHANNEL:
                groups.append({ 'id': dialog.chat.id, 'title': dialog.chat.title })
        
        if current >= total or cur_page*per_page > count:
            break
    
    return groups

async def get_dialogs(cur_page, per_page, count, offset_date, offset_id, offset_peer, limit):
    print(f'[{datetime.now()}] Getting dialogs {(cur_page+1)*per_page}/{count}...')
    try:
        r = await app.invoke(
            functions.messages.GetDialogs(
                offset_date=offset_date,
                offset_id=offset_id,
                offset_peer=offset_peer,
                limit=limit,
                hash=0
            )
        )
    except FloodWait as e:
        print(f'[{datetime.now()}] Flood wait... TIME: {e.value}sec')
        await sleep(e.value)
        r = await get_dialogs(cur_page, per_page, count, offset_date, offset_id, offset_peer, limit)
    return r

app.run(main())
