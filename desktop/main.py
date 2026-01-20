import flet as ft
import requests
import json

# Конфигурация
API_URL = "http://localhost:8000"


class State:
    """Глобальное состояние приложения"""
    token = None
    user = None
    current_project = None


state = State()


# ============== API HELPERS ==============

def get_headers():
    if state.token:
        return {
            "Authorization": f"Bearer {state.token}",
            "Content-Type": "application/json"
        }
    return {"Content-Type": "application/json"}


def api_login(code):
    try:
        res = requests.post(f"{API_URL}/auth/telegram/complete", json={"code": code})
        if res.status_code == 200:
            state.token = res.json()["access_token"]
            res_me = requests.get(f"{API_URL}/users/me", headers=get_headers())
            if res_me.status_code == 200:
                state.user = res_me.json()
            return True, "OK"
        return False, res.json().get("detail", "Ошибка авторизации")
    except Exception as e:
        return False, str(e)


def api_get_me():
    try:
        res = requests.get(f"{API_URL}/users/me", headers=get_headers())
        if res.status_code == 200:
            state.user = res.json()
            return state.user
        return None
    except:
        return None


def api_update_me(name, bio, skills):
    try:
        data = {"name": name, "bio": bio, "skills": skills}
        res = requests.put(f"{API_URL}/users/me", headers=get_headers(), json=data)
        if res.status_code == 200:
            state.user = res.json()
            return True, "Сохранено"
        return False, res.json().get("detail", "Ошибка")
    except Exception as e:
        return False, str(e)


def api_get_users():
    try:
        res = requests.get(f"{API_URL}/users/", headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except:
        return []


def api_get_user(user_id):
    try:
        res = requests.get(f"{API_URL}/users/{user_id}", headers=get_headers())
        return res.json() if res.status_code == 200 else None
    except:
        return None


def api_get_projects():
    try:
        res = requests.get(f"{API_URL}/projects/", headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except:
        return []


def api_get_project(project_id):
    try:
        res = requests.get(f"{API_URL}/projects/{project_id}", headers=get_headers())
        return res.json() if res.status_code == 200 else None
    except:
        return None


def api_create_project(name, description, roles):
    try:
        data = {"name": name, "description": description, "roles": roles}
        res = requests.post(f"{API_URL}/projects/", headers=get_headers(), json=data)
        if res.status_code == 200:
            return True, res.json()
        return False, res.json().get("detail", "Ошибка создания")
    except Exception as e:
        return False, str(e)


def api_update_project(project_id, name, description, roles):
    try:
        data = {"name": name, "description": description, "roles": roles}
        res = requests.patch(f"{API_URL}/projects/{project_id}", headers=get_headers(), json=data)
        if res.status_code == 200:
            return True, res.json()
        return False, res.json().get("detail", "Ошибка обновления")
    except Exception as e:
        return False, str(e)


def api_delete_project(project_id):
    try:
        res = requests.delete(f"{API_URL}/projects/{project_id}", headers=get_headers())
        return res.status_code == 200
    except:
        return False


def api_get_members(project_id):
    try:
        res = requests.get(f"{API_URL}/projects/{project_id}/members", headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except:
        return []


def api_add_member(project_id, user_id, role_name=None):
    try:
        url = f"{API_URL}/projects/{project_id}/members/{user_id}"
        if role_name:
            url += f"?role_name={role_name}"
        res = requests.post(url, headers=get_headers())
        return res.status_code == 200
    except:
        return False


def api_remove_member(project_id, user_id):
    try:
        res = requests.delete(f"{API_URL}/projects/{project_id}/members/{user_id}", headers=get_headers())
        return res.status_code == 200
    except:
        return False


def api_ai_match(project_id, top_n=3):
    try:
        res = requests.post(
            f"{API_URL}/ai/match",
            headers=get_headers(),
            json={"project_id": project_id, "top_n": top_n},
            timeout=120
        )
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None


# ============== MAIN APP ==============

def main(page: ft.Page):
    page.title = "TeamMatch Desktop"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 500
    page.window.height = 800
    page.padding = 0

    # Навигация
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.FOLDER, label="Проекты"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Люди"),
            ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="Профиль"),
        ],
        on_change=lambda e: navigate(e.control.selected_index),
    )

    content_area = ft.Container(expand=True, padding=20)

    def show_snack(message, color="green"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    def navigate(index):
        nav_rail.selected_index = index
        if index == 0:
            show_projects()
        elif index == 1:
            show_users()
        elif index == 2:
            show_profile()
        page.update()

    # ============== LOGIN VIEW ==============
    def show_login():
        page.clean()

        code_input = ft.TextField(
            label="Код из Telegram",
            hint_text="Напишите боту /login",
            text_align=ft.TextAlign.CENTER,
            width=300
        )
        error_text = ft.Text(color="red")
        login_btn = ft.Button("Войти", width=200)

        def on_login(e):
            if not code_input.value:
                error_text.value = "Введите код"
                page.update()
                return

            login_btn.disabled = True
            login_btn.text = "Загрузка..."
            page.update()

            success, msg = api_login(code_input.value.strip())

            if success:
                show_main_layout()
            else:
                error_text.value = msg
                login_btn.disabled = False
                login_btn.text = "Войти"
                page.update()

        login_btn.on_click = on_login

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.ROCKET_LAUNCH, size=80, color=ft.Colors.BLUE),
                        ft.Text("TeamMatch", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("Умный подбор команды", size=14, color=ft.Colors.GREY),
                        ft.Divider(height=40, color="transparent"),
                        code_input,
                        login_btn,
                        error_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                expand=True,
                alignment=ft.Alignment.CENTER,
            )
        )

    # ============== MAIN LAYOUT ==============
    def show_main_layout():
        page.clean()
        nav_rail.selected_index = 0

        page.add(
            ft.Row(
                [
                    nav_rail,
                    ft.VerticalDivider(width=1),
                    content_area,
                ],
                expand=True,
            )
        )
        show_projects()

    # ============== PROJECTS VIEW ==============
    def show_projects():
        projects = api_get_projects()

        # Фильтруем только свои проекты для кнопок редактирования
        my_projects = [p for p in projects if p.get("owner_id") == state.user.get("id")]
        other_projects = [p for p in projects if p.get("owner_id") != state.user.get("id")]

        projects_list = ft.ListView(expand=True, spacing=10, padding=10)

        def make_project_card(p, is_owner=False):
            roles = p.get("roles") or []
            total = sum(r.get("count", 0) for r in roles)
            roles_text = ", ".join([f"{r['name']}×{r['count']}" for r in roles[:3]])

            buttons = [
                ft.TextButton("Открыть", on_click=lambda e, pid=p["id"]: show_project_detail(pid))
            ]
            if is_owner:
                buttons.append(ft.TextButton("✏️", on_click=lambda e, pid=p["id"]: show_project_edit(pid)))

            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER_SPECIAL if is_owner else ft.Icons.FOLDER),
                            title=ft.Text(p["name"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"👥 {total} чел. | {roles_text}" if roles_text else "Роли не указаны"),
                        ),
                        ft.Row(buttons, alignment=ft.MainAxisAlignment.END),
                    ]),
                    padding=10,
                )
            )

        # Мои проекты
        if my_projects:
            projects_list.controls.append(
                ft.Text("Мои проекты", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
            )
            for p in my_projects:
                projects_list.controls.append(make_project_card(p, is_owner=True))

        # Другие проекты
        if other_projects:
            projects_list.controls.append(
                ft.Container(
                    ft.Text("Другие проекты", size=16, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(top=20)
                )
            )
            for p in other_projects:
                projects_list.controls.append(make_project_card(p, is_owner=False))

        if not projects:
            projects_list.controls.append(
                ft.Text("Проектов пока нет", italic=True, color=ft.Colors.GREY)
            )

        content_area.content = ft.Column([
            ft.Row([
                ft.Text("Проекты", size=24, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.ADD, on_click=lambda e: show_project_create(), tooltip="Создать проект"),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: show_projects(), tooltip="Обновить"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            projects_list,
        ], expand=True)
        page.update()

    # ============== PROJECT DETAIL ==============
    def show_project_detail(project_id):
        project = api_get_project(project_id)
        if not project:
            show_snack("Проект не найден", "red")
            return

        members = api_get_members(project_id)
        is_owner = project.get("owner_id") == state.user.get("id")
        roles = project.get("roles") or []

        state.current_project = project

        detail_list = ft.ListView(expand=True, spacing=10, padding=10)

        # Описание
        if project.get("description"):
            detail_list.controls.append(
                ft.Card(content=ft.Container(
                    ft.Text(project["description"]),
                    padding=15
                ))
            )

        # Роли
        if roles:
            detail_list.controls.append(ft.Text("Роли", size=18, weight=ft.FontWeight.BOLD))
            for role in roles:
                filled = len([m for m in members if m.get("role_name") == role["name"]])
                skills_text = ", ".join([f"{s['name']}({s['level']}+)" for s in role.get("skills", [])])
                detail_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(role["name"], weight=ft.FontWeight.BOLD),
                                ft.Text(f"{filled}/{role['count']}", 
                                       color=ft.Colors.GREEN if filled >= role["count"] else ft.Colors.ORANGE)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(skills_text or "Навыки не указаны", size=12, color=ft.Colors.GREY),
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=8,
                    )
                )

        # Участники
        detail_list.controls.append(
            ft.Row([
                ft.Text(f"Участники ({len(members)})", size=18, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.PERSON_ADD, on_click=lambda e: show_add_member_dialog(), 
                             tooltip="Добавить участника") if is_owner else ft.Container(),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        if members:
            for m in members:
                detail_list.controls.append(
                    ft.Card(content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(m.get("name") or m.get("username") or f"User #{m['id']}", 
                                       weight=ft.FontWeight.BOLD),
                                ft.Text(m.get("role_name") or "Без роли", size=12, color=ft.Colors.GREY),
                            ], expand=True),
                            ft.IconButton(
                                ft.Icons.REMOVE_CIRCLE,
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, uid=m["id"]: remove_member(uid),
                                tooltip="Удалить"
                            ) if is_owner else ft.Container(),
                        ]),
                        padding=10,
                    ))
                )
        else:
            detail_list.controls.append(ft.Text("Нет участников", italic=True, color=ft.Colors.GREY))

        # AI подбор (только для владельца с ролями)
        if is_owner and roles:
            detail_list.controls.append(ft.Divider(height=20))
            detail_list.controls.append(
                ft.Button(
                    "🤖 AI Подбор команды",
                    on_click=lambda e: show_ai_match(project_id),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                    width=250,
                )
            )

        def remove_member(user_id):
            if api_remove_member(project_id, user_id):
                show_snack("Участник удалён")
                show_project_detail(project_id)
            else:
                show_snack("Ошибка удаления", "red")

        def show_add_member_dialog():
            users = api_get_users()
            member_ids = [m["id"] for m in members]
            available = [u for u in users if u["id"] not in member_ids and u["id"] != project.get("owner_id")]

            if not available:
                show_snack("Нет доступных пользователей", "orange")
                return

            user_dropdown = ft.Dropdown(
                label="Пользователь",
                options=[ft.dropdown.Option(str(u["id"]), u.get("name") or u.get("username") or f"User #{u['id']}") 
                        for u in available],
                width=250,
            )
            role_dropdown = ft.Dropdown(
                label="Роль",
                options=[ft.dropdown.Option(r["name"]) for r in roles] if roles else [],
                width=250,
            )

            def on_add(e):
                if not user_dropdown.value:
                    return
                if api_add_member(project_id, int(user_dropdown.value), role_dropdown.value):
                    show_snack("Участник добавлен")
                    dialog.open = False
                    page.update()
                    show_project_detail(project_id)
                else:
                    show_snack("Ошибка добавления", "red")

            dialog = ft.AlertDialog(
                title=ft.Text("Добавить участника"),
                content=ft.Column([user_dropdown, role_dropdown], tight=True, spacing=15),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: close_dialog()),
                    ft.Button("Добавить", on_click=on_add),
                ],
            )

            def close_dialog():
                dialog.open = False
                page.update()

            page.dialog = dialog
            dialog.open = True
            page.update()

        # Кнопки управления
        action_buttons = [ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_projects())]
        if is_owner:
            action_buttons.extend([
                ft.IconButton(ft.Icons.EDIT, on_click=lambda e: show_project_edit(project_id), tooltip="Редактировать"),
                ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, 
                             on_click=lambda e: confirm_delete_project(project_id), tooltip="Удалить"),
            ])

        content_area.content = ft.Column([
            ft.Row([
                ft.Row(action_buttons),
                ft.Text(project["name"], size=22, weight=ft.FontWeight.BOLD, expand=True),
            ], alignment=ft.MainAxisAlignment.START),
            detail_list,
        ], expand=True)
        page.update()

    def confirm_delete_project(project_id):
        def on_confirm(e):
            if api_delete_project(project_id):
                show_snack("Проект удалён")
                dialog.open = False
                page.update()
                show_projects()
            else:
                show_snack("Ошибка удаления", "red")

        dialog = ft.AlertDialog(
            title=ft.Text("Удалить проект?"),
            content=ft.Text("Это действие нельзя отменить."),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: (setattr(dialog, 'open', False), page.update())),
                ft.Button("Удалить", bgcolor=ft.Colors.RED, color="white", on_click=on_confirm),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    # ============== PROJECT CREATE/EDIT ==============
    def show_project_create():
        show_project_form(None)

    def show_project_edit(project_id):
        project = api_get_project(project_id)
        if project:
            show_project_form(project)

    def show_project_form(project=None):
        is_edit = project is not None

        name_input = ft.TextField(label="Название проекта", value=project["name"] if project else "")
        desc_input = ft.TextField(label="Описание", multiline=True, min_lines=3, 
                                  value=project.get("description", "") if project else "")

        # Роли
        roles_list = ft.Column(spacing=10)
        current_roles = list(project.get("roles") or []) if project else []

        def refresh_roles_ui():
            roles_list.controls.clear()
            for i, role in enumerate(current_roles):
                skills_text = ", ".join([f"{s['name']}({s['level']})" for s in role.get("skills", [])])
                roles_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{role['name']} × {role['count']}", weight=ft.FontWeight.BOLD),
                                ft.Text(skills_text or "Без навыков", size=12, color=ft.Colors.GREY),
                            ], expand=True),
                            ft.IconButton(ft.Icons.EDIT, on_click=lambda e, idx=i: edit_role(idx)),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, 
                                         on_click=lambda e, idx=i: delete_role(idx)),
                        ]),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=8,
                    )
                )
            page.update()

        def delete_role(index):
            current_roles.pop(index)
            refresh_roles_ui()

        def edit_role(index):
            show_role_dialog(current_roles[index], index)

        def show_role_dialog(role=None, index=None):
            role_name = ft.TextField(label="Название роли", value=role["name"] if role else "", width=250)
            role_count = ft.TextField(label="Кол-во", value=str(role["count"]) if role else "1", width=80)
            
            skills_data = list(role.get("skills", [])) if role else []
            skills_column = ft.Column(spacing=5)

            def refresh_skills():
                skills_column.controls.clear()
                for j, sk in enumerate(skills_data):
                    skills_column.controls.append(
                        ft.Row([
                            ft.Text(f"{sk['name']} ({sk['level']})", expand=True),
                            ft.IconButton(ft.Icons.CLOSE, on_click=lambda e, jj=j: remove_skill(jj)),
                        ])
                    )
                page.update()

            def remove_skill(j):
                skills_data.pop(j)
                refresh_skills()

            skill_name_input = ft.TextField(label="Навык", width=150)
            skill_level_input = ft.TextField(label="Уровень", value="5", width=60)

            def add_skill(e):
                if skill_name_input.value:
                    skills_data.append({
                        "name": skill_name_input.value,
                        "level": int(skill_level_input.value or 5)
                    })
                    skill_name_input.value = ""
                    refresh_skills()

            refresh_skills()

            def on_save(e):
                if not role_name.value:
                    return
                new_role = {
                    "name": role_name.value,
                    "count": int(role_count.value or 1),
                    "skills": skills_data
                }
                if index is not None:
                    current_roles[index] = new_role
                else:
                    current_roles.append(new_role)
                dialog.open = False
                page.update()
                refresh_roles_ui()

            dialog = ft.AlertDialog(
                title=ft.Text("Роль" if index is None else "Редактировать роль"),
                content=ft.Column([
                    ft.Row([role_name, role_count]),
                    ft.Divider(),
                    ft.Text("Навыки:", weight=ft.FontWeight.BOLD),
                    skills_column,
                    ft.Row([skill_name_input, skill_level_input, 
                           ft.IconButton(ft.Icons.ADD, on_click=add_skill)]),
                ], tight=True, scroll=ft.ScrollMode.AUTO, width=350, height=300),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: (setattr(dialog, 'open', False), page.update())),
                    ft.Button("Сохранить", on_click=on_save),
                ],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        refresh_roles_ui()

        def on_save_project(e):
            if not name_input.value:
                show_snack("Введите название", "red")
                return

            roles_to_save = current_roles if current_roles else None

            if is_edit:
                success, result = api_update_project(
                    project["id"], name_input.value, desc_input.value, roles_to_save
                )
            else:
                success, result = api_create_project(
                    name_input.value, desc_input.value, roles_to_save
                )

            if success:
                show_snack("Сохранено!")
                show_projects()
            else:
                show_snack(str(result), "red")

        content_area.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_projects()),
                ft.Text("Редактировать проект" if is_edit else "Новый проект", 
                       size=22, weight=ft.FontWeight.BOLD),
            ]),
            ft.ListView(
                controls=[
                    name_input,
                    desc_input,
                    ft.Divider(height=20),
                    ft.Row([
                        ft.Text("Роли", size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(ft.Icons.ADD, on_click=lambda e: show_role_dialog(), tooltip="Добавить роль"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    roles_list,
                    ft.Divider(height=20),
                    ft.Button(
                        "Сохранить" if is_edit else "Создать",
                        on_click=on_save_project,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                        width=200,
                    ),
                ],
                expand=True,
                padding=10,
                spacing=15,
            ),
        ], expand=True)
        page.update()

    # ============== AI MATCH ==============
    def show_ai_match(project_id):
        # Показываем лоадер
        content_area.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_project_detail(project_id)),
                ft.Text("AI Подбор", size=22, weight=ft.FontWeight.BOLD),
            ]),
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text("AI анализирует кандидатов...", size=16),
                    ft.Text("Это может занять до минуты", size=12, color=ft.Colors.GREY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                expand=True,
                alignment=ft.Alignment.CENTER,
            )
        ], expand=True)
        page.update()

        # Запрос
        results = api_ai_match(project_id, top_n=3)

        if results is None:
            content_area.content = ft.Column([
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_project_detail(project_id)),
                    ft.Text("Ошибка", size=22, weight=ft.FontWeight.BOLD),
                ]),
                ft.Container(
                    ft.Text("Не удалось получить результаты от AI", color=ft.Colors.RED),
                    expand=True, alignment=ft.Alignment.CENTER,
                )
            ], expand=True)
            page.update()
            return

        # Отображаем результаты
        results_list = ft.ListView(expand=True, spacing=10, padding=10)

        all_users = api_get_users()
        members = api_get_members(project_id)
        member_ids = [m["id"] for m in members]

        for role_result in results:
            role_name = role_result.get("role_name", "?")
            needed = role_result.get("needed", 0)
            filled = role_result.get("filled", 0)
            candidates = role_result.get("candidates", [])

            results_list.controls.append(
                ft.Container(
                    ft.Row([
                        ft.Text(role_name, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{filled}/{needed}", 
                               color=ft.Colors.GREEN if filled >= needed else ft.Colors.ORANGE),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    margin=ft.margin.only(top=15, bottom=5),
                )
            )

            if not candidates:
                results_list.controls.append(
                    ft.Text("Подходящих кандидатов не найдено", italic=True, color=ft.Colors.GREY)
                )
                continue

            for c in candidates:
                user_data = next((u for u in all_users if u["id"] == c["id"]), None)
                user_name = user_data.get("name") or user_data.get("username") or f"User #{c['id']}" if user_data else f"User #{c['id']}"
                score = c.get("score", 0)
                reason = c.get("reason", "")

                is_member = c["id"] in member_ids

                score_color = ft.Colors.GREEN if score >= 70 else ft.Colors.ORANGE if score >= 40 else ft.Colors.RED

                def make_add_handler(cid, rname):
                    def handler(e):
                        if api_add_member(project_id, cid, rname):
                            show_snack(f"Добавлен в команду!")
                            show_ai_match(project_id)  # Обновляем
                        else:
                            show_snack("Ошибка", "red")
                    return handler

                results_list.controls.append(
                    ft.Card(content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(user_name, weight=ft.FontWeight.BOLD),
                                ft.Text(reason, size=12, color=ft.Colors.GREY_700),
                            ], expand=True),
                            ft.Column([
                                ft.Text(f"{score}%", size=20, weight=ft.FontWeight.BOLD, color=score_color),
                                ft.Text("✓ В команде", size=10, color=ft.Colors.GREEN) if is_member 
                                else ft.TextButton("Добавить", on_click=make_add_handler(c["id"], role_name)),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END),
                        ]),
                        padding=12,
                    ))
                )

        content_area.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_project_detail(project_id)),
                ft.Text("Результаты AI подбора", size=22, weight=ft.FontWeight.BOLD),
            ]),
            results_list,
        ], expand=True)
        page.update()

    # ============== USERS VIEW ==============
    def show_users():
        users = api_get_users()

        users_list = ft.ListView(expand=True, spacing=10, padding=10)

        for u in users:
            skills = u.get("skills") or []
            skills_text = ", ".join([s["name"] for s in skills[:4]])
            is_me = u["id"] == state.user.get("id")

            users_list.controls.append(
                ft.Card(content=ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE if is_me else None),
                        title=ft.Text(
                            (u.get("name") or u.get("username") or f"User #{u['id']}") + (" (вы)" if is_me else ""),
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(skills_text or "Навыки не указаны", size=12),
                        on_click=lambda e, uid=u["id"]: show_user_detail(uid),
                    ),
                    padding=5,
                ))
            )

        if not users:
            users_list.controls.append(ft.Text("Пользователей нет", italic=True))

        content_area.content = ft.Column([
            ft.Row([
                ft.Text("Пользователи", size=24, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: show_users()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            users_list,
        ], expand=True)
        page.update()

    def show_user_detail(user_id):
        user = api_get_user(user_id)
        if not user:
            show_snack("Пользователь не найден", "red")
            return

        skills = user.get("skills") or []

        skills_chips = ft.Row(wrap=True, spacing=5)
        for s in skills:
            color = ft.Colors.GREEN if s["level"] >= 7 else ft.Colors.ORANGE if s["level"] >= 4 else ft.Colors.RED
            skills_chips.controls.append(
                ft.Chip(label=ft.Text(f"{s['name']} ({s['level']})"), bgcolor=color)
            )

        content_area.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_users()),
                ft.Text("Профиль пользователя", size=22, weight=ft.FontWeight.BOLD),
            ]),
            ft.ListView(
                controls=[
                    ft.Card(content=ft.Container(
                        content=ft.Column([
                            ft.Text(user.get("name") or "Без имени", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(f"@{user.get('username')}" if user.get("username") else "Без username", 
                                   color=ft.Colors.GREY),
                            ft.Divider(),
                            ft.Text("О себе:", weight=ft.FontWeight.BOLD),
                            ft.Text(user.get("bio") or "Не указано"),
                            ft.Divider(),
                            ft.Text("Навыки:", weight=ft.FontWeight.BOLD),
                            skills_chips if skills else ft.Text("Не указаны", italic=True),
                        ], spacing=10),
                        padding=20,
                    )),
                ],
                expand=True,
                padding=10,
            ),
        ], expand=True)
        page.update()

    # ============== PROFILE VIEW ==============
    def show_profile():
        user = state.user or {}

        name_input = ft.TextField(label="Имя", value=user.get("name", ""))
        bio_input = ft.TextField(label="О себе", multiline=True, min_lines=3, value=user.get("bio", ""))

        current_skills = list(user.get("skills") or [])
        skills_column = ft.Column(spacing=5)

        def refresh_skills():
            skills_column.controls.clear()
            for i, s in enumerate(current_skills):
                level_color = ft.Colors.GREEN if s["level"] >= 7 else ft.Colors.ORANGE if s["level"] >= 4 else ft.Colors.RED
                skills_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(s["name"], expand=True),
                            ft.Text(f"{s['level']}/10", color=level_color, weight=ft.FontWeight.BOLD),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, 
                                         on_click=lambda e, idx=i: remove_skill(idx)),
                        ]),
                        bgcolor=ft.Colors.GREY_100,
                        padding=8,
                        border_radius=5,
                    )
                )
            page.update()

        def remove_skill(idx):
            current_skills.pop(idx)
            refresh_skills()

        skill_name = ft.TextField(label="Навык", width=150)
        skill_level = ft.Slider(min=0, max=10, value=5, divisions=10, label="{value}", width=150)

        def add_skill(e):
            if skill_name.value:
                current_skills.append({"name": skill_name.value, "level": int(skill_level.value)})
                skill_name.value = ""
                refresh_skills()

        refresh_skills()

        def on_save(e):
            success, msg = api_update_me(name_input.value, bio_input.value, current_skills)
            if success:
                show_snack("Профиль сохранён!")
            else:
                show_snack(msg, "red")

        def on_logout(e):
            state.token = None
            state.user = None
            show_login()

        content_area.content = ft.Column([
            ft.Row([
                ft.Text("Мой профиль", size=24, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.LOGOUT, on_click=on_logout, tooltip="Выйти"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ListView(
                controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Telegram ID: {user.get('telegram_id', '?')}", color=ft.Colors.GREY),
                            ft.Text(f"Username: @{user.get('username', '—')}", color=ft.Colors.GREY),
                        ]),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=8,
                    ),
                    name_input,
                    bio_input,
                    ft.Divider(height=20),
                    ft.Text("Навыки", size=18, weight=ft.FontWeight.BOLD),
                    skills_column,
                    ft.Row([skill_name, skill_level, ft.IconButton(ft.Icons.ADD, on_click=add_skill)]),
                    ft.Divider(height=20),
                    ft.Button(
                        "Сохранить",
                        on_click=on_save,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                        width=200,
                    ),
                ],
                expand=True,
                padding=10,
                spacing=15,
            ),
        ], expand=True)
        page.update()

    # ============== START ==============
    show_login()


# Запуск
ft.app(target=main)