import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class KönigsbergBridgesGame:
    def __init__(self):
        self.graph = nx.MultiGraph()
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.pos = None
        
        self.areas = {
            'A': "Северный берег реки Преголя",
            'B': "Южный берег реки Преголя", 
            'C': "Остров Кнайпхоф",
            'D': "Остров Ломзе"
        }
        
        self.bridges = [
            ('A', 'C', {'name': 'Зеленый мост', 'color': 'green'}),
            ('A', 'C', {'name': 'Медовый мост', 'color': 'gold'}),
            ('A', 'D', {'name': 'Деревянный мост', 'color': 'brown'}),
            ('B', 'C', {'name': 'Высокий мост', 'color': 'blue'}),
            ('B', 'C', {'name': 'Кузнечный мост', 'color': 'black'}),
            ('B', 'D', {'name': 'Лавочный мост', 'color': 'orange'}),
            ('C', 'D', {'name': 'Императорский мост', 'color': 'purple'})
        ]
        
        for a, b, data in self.bridges:
            self.graph.add_edge(a, b, **data)
        
        self.used_bridges = set()
        self.current_position = None
        self.path_history = []
    
    def initialize_visualization(self):
        """Инициализирует позиции узлов для стабильной визуализации"""
        self.pos = nx.spring_layout(self.graph)
        self.update_visualization()
    
    def update_visualization(self, highlight_edges=None, current_node=None):
        """Обновляет графическое отображение графа"""
        self.ax.clear()
        
        # Рисуем узлы
        node_colors = ['red' if n == current_node else 'skyblue' for n in self.graph.nodes()]
        nx.draw_networkx_nodes(self.graph, self.pos, ax=self.ax, 
                             node_size=2000, node_color=node_colors)
        
        # Рисуем все мосты с разными стилями
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            edge = (u, v, key)
            if edge in self.used_bridges:
                # Пройденные мосты
                edge_color = 'gray'
                edge_style = 'dashed'
                edge_width = 1
            elif highlight_edges and edge in highlight_edges:
                # Доступные мосты
                edge_color = 'lime'
                edge_style = 'solid' 
                edge_width = 3
            else:
                # Непройденные мосты
                edge_color = data['color']
                edge_style = 'solid'
                edge_width = 2
            
            nx.draw_networkx_edges(
                self.graph, self.pos, ax=self.ax,
                edgelist=[(u, v)],
                width=edge_width,
                edge_color=edge_color,
                style=edge_style
            )
        
        # Подписи узлов
        labels = {k: f"{k}\n({v})" for k, v in self.areas.items()}
        nx.draw_networkx_labels(self.graph, self.pos, ax=self.ax, 
                              labels=labels, font_size=10)
        
        # Подписи мостов
        edge_labels = {(u, v, key): data['name'] 
                      for u, v, key, data in self.graph.edges(keys=True, data=True)}
        nx.draw_networkx_edge_labels(
            self.graph, self.pos, ax=self.ax,
            edge_labels=edge_labels,
            font_size=8,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )
        
        # История переходов
        if self.path_history:
            history_text = "Ваш путь:\n" + "\n".join(
                f"{i+1}. {name}: {u} → {v}" 
                for i, (u, v, name) in enumerate(self.path_history[-5:])
            )
            self.ax.text(
                1.05, 0.5, history_text,
                transform=self.ax.transAxes,
                verticalalignment='center',
                bbox=dict(facecolor='white', alpha=0.5)
            )
        
        self.ax.set_title("Мосты Кенигсберга (задача Эйлера)")
        self.ax.axis('off')
        
        plt.draw()
        plt.pause(0.1)
    
    def check_eulerian_path(self):
        """Проверяет существование эйлерова пути"""
        degrees = dict(self.graph.degree())
        odd_degree_count = sum(1 for degree in degrees.values() if degree % 2 != 0)
        return odd_degree_count == 0 or odd_degree_count == 2
    
    def find_eulerian_path(self):
        """Пытается найти эйлеров путь"""
        try:
            return list(nx.eulerian_path(self.graph))
        except nx.NetworkXError:
            return None
    
    def interactive_walk(self):
        """Интерактивный режим прохождения"""
        print("\n--- ИНТЕРАКТИВНЫЙ РЕЖИМ ---")
        print("Попробуйте пройти по всем мостам без повторений!")
        print("Введите номер моста или 'Q' для выхода\n")
        
        self.used_bridges = set()
        self.current_position = 'A'
        self.path_history = []
        self.initialize_visualization()
        
        while True:
            print(f"\nВы находитесь в: {self.areas[self.current_position]} ({self.current_position})")
            
            available_bridges = []
            for u, v, key in self.graph.edges(self.current_position, keys=True):
                bridge_id = (u, v, key)
                if bridge_id not in self.used_bridges:
                    data = self.graph.get_edge_data(u, v, key)
                    direction = v if u == self.current_position else u
                    available_bridges.append((bridge_id, data['name'], direction))
            
            if not available_bridges:
                print("Нет доступных мостов отсюда!")
                break
            
            print("Доступные мосты:")
            for i, (bridge_id, name, direction) in enumerate(available_bridges, 1):
                print(f"{i}. {name} -> {self.areas[direction]} ({direction})")
            
            # Обновляем визуализацию с подсветкой
            self.update_visualization(
                highlight_edges=[bridge_id for bridge_id, _, _ in available_bridges],
                current_node=self.current_position
            )
            
            choice = input("Ваш выбор: ").strip().upper()
            
            if choice == 'Q':
                print("Выход из режима")
                return
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_bridges):
                    bridge_id, bridge_name, next_area = available_bridges[choice_idx]
                else:
                    print("Неверный номер!")
                    continue
                
                self.used_bridges.add(bridge_id)
                self.path_history.append((self.current_position, next_area, bridge_name))
                self.current_position = next_area
                
                print(f"Переход по {bridge_name} в {self.areas[next_area]}")
                self.update_visualization(current_node=self.current_position)
                
                if len(self.used_bridges) == len(self.bridges):
                    print("\nПОЗДРАВЛЯЕМ! Вы прошли все мосты!")
                    return
                
            except ValueError:
                print("Введите номер или Q!")
    
    def validate_user_path(self, path):
        """Проверяет корректность введенного пути"""
        used_bridges = set()
        current_position = path[0][0] if path else None
        
        for i, (u, v, name) in enumerate(path):
            if u != current_position:
                return False, f"Ошибка шага {i+1}: нельзя перейти из {current_position} в {u}"
            
            bridge_found = False
            for edge in self.graph.edges(data=True, keys=True):
                if edge[3]['name'] == name and ((edge[0] == u and edge[1] == v) or (edge[0] == v and edge[1] == u)):
                    bridge_id = (edge[0], edge[1], edge[2])
                    if bridge_id in used_bridges:
                        return False, f"Мост {name} уже использован (шаг {i+1})"
                    used_bridges.add(bridge_id)
                    bridge_found = True
                    break
            
            if not bridge_found:
                return False, f"Моста {name} между {u} и {v} не существует"
            
            current_position = v
        
        if len(used_bridges) == len(self.bridges):
            return True, "Великолепно! Все мосты пройдены!"
        else:
            return False, f"Пройдено {len(used_bridges)}/{len(self.bridges)} мостов"
    
    def manual_path_input(self):
        """Режим ручного ввода маршрута"""
        print("\n--- РЕЖИМ РУЧНОГО ВВОДА ---")
        print("Формат: Начало, Конец, Название моста")
        print("Пример: A, C, Зеленый мост")
        print("Введите 'Готово' для завершения\n")
        
        path = []
        self.initialize_visualization()
        
        while True:
            self.update_visualization()
            user_input = input("Введите переход: ").strip()
            
            if user_input.lower() == 'готово':
                break
            
            try:
                parts = [p.strip() for p in user_input.split(',')]
                if len(parts) != 3:
                    print("Нужно 3 значения через запятую!")
                    continue
                
                u, v, name = parts
                if u not in self.areas or v not in self.areas:
                    print("Ошибка в обозначениях областей!")
                    continue
                
                path.append((u.upper(), v.upper(), name))
                
                # Валидация и визуализация
                is_valid, msg = self.validate_user_path(path)
                if not is_valid and "уже использован" not in msg and "не существует" not in msg:
                    print(f"Ошибка: {msg}")
                    path.pop()
                else:
                    self.path_history = path.copy()
                    self.used_bridges = set()
                    for step in path:
                        for edge in self.graph.edges(data=True, keys=True):
                            if edge[3]['name'] == step[2] and ((edge[0] == step[0] and edge[1] == step[1]) or (edge[0] == step[1] and edge[1] == step[0])):
                                self.used_bridges.add((edge[0], edge[1], edge[2]))
                                break
                    self.current_position = path[-1][1]
                    self.update_visualization(current_node=self.current_position)
                    
            except Exception as e:
                print(f"Ошибка ввода: {e}")
        
        is_valid, message = self.validate_user_path(path)
        print("\nРезультат проверки:")
        print(message)
    
    def play(self):
        """Основной игровой цикл"""
        print("=== КЕНИГСБЕРГСКИЕ МОСТЫ ===")
        print("Цель: пройти все 7 мостов без повторений")
        
        # Первая визуализация
        self.initialize_visualization()
        
        print("\nРайоны города:")
        for area, desc in self.areas.items():
            print(f"{area}: {desc}")
        
        print("\nМосты:")
        for i, (a, b, data) in enumerate(self.bridges, 1):
            print(f"{i}. {data['name']} ({a}-{b})")
        
        print("\nАвтоматическая проверка...")
        if self.check_eulerian_path():
            path = self.find_eulerian_path()
            if path:
                print("\nТеоретически возможный маршрут:")
                for i, (u, v) in enumerate(path, 1):
                    edge_data = self.graph.get_edge_data(u, v)
                    first_key = next(iter(edge_data))
                    print(f"{i}. {edge_data[first_key]['name']}: {u} → {v}")
            else:
                print("\nНе найдено подходящего пути")
        else:
            print("\nЭйлеров путь невозможен (исторически корректный результат)")
        
        # Меню режимов
        while True:
            print("\nВыберите режим:")
            print("1. Интерактивное прохождение")
            print("2. Ручной ввод маршрута")
            print("3. Повторить теорию")
            print("4. Выход")
            
            choice = input("Ваш выбор: ").strip()
            
            if choice == '1':
                self.interactive_walk()
            elif choice == '2':
                self.manual_path_input()
            elif choice == '3':
                path = self.find_eulerian_path()
                if path:
                    print("\nТеоретический маршрут:")
                    for i, (u, v) in enumerate(path, 1):
                        edge_data = self.graph.get_edge_data(u, v)
                        first_key = next(iter(edge_data))
                        print(f"{i}. {edge_data[first_key]['name']}: {u} → {v}")
                else:
                    print("\nПуть невозможен (нечетные степени вершин: A=3, B=3, C=5, D=3)")
            elif choice == '4':
                plt.close()
                break
            else:
                print("Неверный ввод!")
        
        print("\nИсторическая справка:")
        print("Леонард Эйлер доказал в 1736 году, что такой путь невозможен")
        print("и заложил основы теории графов. В Кенигсберге 4 вершины")
        print("с нечетными степенями, что делает задачу нерешаемой.")

if __name__ == "__main__":
    game = KönigsbergBridgesGame()
    game.play()