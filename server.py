"""Todos Service With HTMX Demo

TODO
1. Escape content!
2. Move index.html into file
3. Add comments
4. Merge README.md into here with tradeoff discussion
5. Use transactions with database


BENEFITS
1. Javascript is optional!
2. Less than a hundred lines of code: client + server

"""

import contextlib
import html
import http.server
import pathlib
import sqlite3
import urllib.parse

    
class TodosHandler(http.server.SimpleHTTPRequestHandler):

    index_html = (pathlib.Path(__file__).parent / 'index.html').read_text()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        con = sqlite3.connect('todos.sqlite3', isolation_level=None)
        con.row_factory = sqlite3.Row
        query = """
            SELECT rowid, content FROM todos WHERE path = ? ORDER BY rowid DESC
        """
        cursor = con.execute(query, (url.path,))
        rows = cursor.fetchall()
        self.send_response(200)
        self.end_headers()
        list_item = """
            <li>
              {content}
              <form method="post" hx-post="" hx-select="#items"
               hx-target="#items" hx-swap="outerHTML">
                <button type="submit" name="delete" value="{rowid}" />
              </form>
            </li>
        """
        todos = '\n'.join(map(list_item.format_map, rows))
        response = self.index_html.format(todos=todos)
        self.wfile.write(response.encode('utf-8'))

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(body)
        con = sqlite3.connect('todos.sqlite3', isolation_level=None)
        if 'insert' in data:
            todo, = data['insert']
            query = 'INSERT INTO todos VALUES (?, ?, ?)'
            con.execute(query, (url.path, todo, False))
        if 'delete' in data:
            rowid, = data['delete']
            query = 'DELETE FROM todos WHERE rowid = ?'
            con.execute(query, (int(rowid),))
        self.send_response(303)
        self.send_header('Location', self.path)
        self.end_headers()


def main():
    con = sqlite3.connect('todos.sqlite3', isolation_level=None)
    con.execute('CREATE TABLE IF NOT EXISTS todos (path, content)')
    server_address = ('', 8000)
    httpd = http.server.ThreadingHTTPServer(server_address, TodosHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
