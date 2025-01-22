import flet as ft
import sqlite3  


class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        #self.page.bgcolor = 'white'
        self.page.window.width = 350
        self.page.window.height = 450
        self.page.window.resizable = False
        self.page.window.always_on_top = True
        self.page.title = 'ToDo App'
        self.task= ''
        self.view = 'all'
        self.db_exec('CREATE TABLE IF NOT EXISTS tasks(name, status)')
        self.results = self.db_exec('SELECT * FROM tasks')
        self.main_page()

    def db_exec(self, query, params=[]):
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()

    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label

        if is_checked:
            self.db_exec('UPDATE tasks SET status = "complete" WHERE name = ?', params=[label])
        else:
            self.db_exec('UPDATE tasks SET status = "incomplete" WHERE name = ?', params=[label])

        if self.view == 'all':
            self.results = self.db_exec('SELECT * FROM tasks')
        else: 
            self.results = self.db_exec('SELECT * FROM tasks WHERE status = ?', params=[self.view])
        
        self.update_task_list()

    def tabs_changed(self, e):
        if e.control.selected_index == 0:
            self.results = self.db_exec('SELECT * FROM tasks')
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_exec('SELECT * FROM tasks WHERE status = "incomplete"')
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_exec('SELECT * FROM tasks WHERE status = "complete"')
            self.view = 'complete'
            
        self.update_task_list()
        
    
    def tasks_container(self):
        return ft.Container(
            height = self.page.height * 0.8,
            content= ft.Column(
                        controls=[
                            ft.Checkbox(label=res[0], on_change= self.checked, value = True if res[1] == 'complete' else False)
                            for res in self.results if res
                        ]
                    ) 
        )

    def set_value(self, e):
        self.task = e.control.value

    def add(self, e, input_task):
        name = self.task
        status = 'incomplete'
    
        if name:
            self.db_exec(query='INSERT INTO tasks VALUES(?, ?)', params=[name, status])
            input_task.value = ''
            self.results = self.db_exec('SELECT * FROM tasks')
            self.update_task_list()

    def update_task_list(self):
        tasks = self.tasks_container()
        self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()

    def main_page(self):
        input_task = ft.TextField(hint_text='Digite uma tarefa', expand=True, on_change=self.set_value)
        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=lambda e: self.add(e, input_task)),
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text='Todos'),
                ft.Tab(text='Em andamento'),
                ft.Tab(text='Finalizados')
            ]
        )

        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)
    



ft.app(target = ToDo)