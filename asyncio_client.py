import asyncio
import curses
import string
from itertools import chain


class ChatWindow():
    HOST = '127.0.0.1'
    PORT = 5355
    TITLE = 'Chat'
    USERNAME = 'bot'

    def __init__(self):
        self.reader = None
        self.writer = None
        self.stdscr = curses.initscr()
        self.cursor_x = 0
        self.current_mesage = ''
        self.messages = []

    def start(self):
        self.stdscr.clear()
        self.stdscr.refresh()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def stop(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        self.writer.close()

    def get_message_text(self, message):
        message = message.strip()
        message = message.replace('\t', '    ')
        return f'[{self.USERNAME}]: {message}'

    def format_message(self, message):
        lines = 0
        current_line_width = 0
        result = ''
        for c in message:
            current_line_width += 1
            if c == '\n':
                current_line_width = 0
                lines += 1
            elif current_line_width == self.width - 2:
                result += '\n'
                lines += 1
                current_line_width = 1
            result += c
        return result, lines, current_line_width

    @property
    def height(self):
        return self.stdscr.getmaxyx()[0]

    @property
    def width(self):
        return self.stdscr.getmaxyx()[1]

    def draw_title(self):
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.attron(curses.A_BOLD)
        title = f'Welcome, {self.USERNAME}'
        start_x_title = int((self.width // 2) - (len(title) // 2) - len(title) % 2)
        self.stdscr.addstr(0, start_x_title, title)
        self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.attroff(curses.A_BOLD)

    def draw_messages(self):
        result = []

        current_message_text = self.get_message_text(self.current_mesage)
        input_text, lines, last_line_size = self.format_message(current_message_text)

        for message in self.messages:
            formatted_message = self.format_message(message)[0]
            result.extend(formatted_message.split('\n'))

        lines_to_draw = self.height - lines - 4

        messages = result[-lines_to_draw:]
        self.stdscr.addstr(2, 0, '\n'.join(messages))

    def draw_input(self):
        self.stdscr.attron(curses.color_pair(2))
        message_text = self.get_message_text(self.current_mesage)
        input_text, lines, last_line_size = self.format_message(message_text)
        self.stdscr.addstr(self.height - lines - 1, 0, input_text)
        self.stdscr.move(self.height - 1, last_line_size)
        self.stdscr.attroff(curses.color_pair(2))

    def redraw(self):
        self.stdscr.clear()
        self.draw_title()
        self.draw_messages()
        self.draw_input()
        self.stdscr.refresh()

    def send_message(self):
        self.messages.append(self.get_message_text(self.current_mesage))
        self.writer.write(self.get_message_text(self.current_mesage).encode())
        self.current_mesage = ''
        self.redraw()

    async def run(self):
        k = 0
        while True:
            if k == ord('\n'):
                self.send_message()
                self.redraw()

            elif k == curses.KEY_BACKSPACE:
                self.current_mesage = self.current_mesage[:-1]
            elif k != 0:
                char = chr(k)
                if char in chain(string.digits, string.ascii_letters, string.whitespace):
                    self.current_mesage += char
            self.redraw()
            k = self.stdscr.getch()
            await asyncio.sleep(1/1000)


    async def receive_message(self):
        while True:
            data = await self.reader.read(100)
            self.messages.append(data.decode().split('\n'))

    async def main(self):
        self.reader, self.writer = await asyncio.open_connection(self.HOST, self.PORT)
        self.start()
        self.writer.write(f'{self.USERNAME} connected to chat \n'.encode())
        # self.redraw()
        await asyncio.gather(self.run(), self.receive_message())

if __name__ == "__main__":
    asyncio.run(ChatWindow().main())
