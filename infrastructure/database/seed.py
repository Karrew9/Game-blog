from sqlalchemy.orm import Session

from core.security import hash_password
from infrastructure.database.models import UserModel, PostModel, CommentModel
from datetime import datetime, timedelta

def seed_database(session: Session):
    session.query(CommentModel).delete()
    session.query(PostModel).delete()
    session.query(UserModel).delete()
    session.commit()

    users = [
        UserModel(
            username="CyberNinja42",
            email="ivan@example.com",
            password_hash=hash_password("SecurePass123!"),
            is_active=True,
            avatar_path="/static/images/default-avatar.png",
            bio="Профессиональный игрок и рецензент игр",
            created_at=datetime.utcnow() - timedelta(days=10),
            last_login=datetime.utcnow() - timedelta(hours=2)
        ),
        UserModel(
            username="PixelQueenX",
            email="anna@example.com",
            password_hash=hash_password("AnnaGaming2024"),
            is_active=True,
            avatar_path="/static/images/default-avatar.png",
            bio="Люблю инди-игры и пиксельную графику",
            created_at=datetime.utcnow() - timedelta(days=7),
            last_login=datetime.utcnow() - timedelta(days=1)
        ),
        UserModel(
            username="ThunderBolt_Gaming",
            email="alex@example.com",
            password_hash=hash_password("ThunderAlex!"),
            is_active=True,
            avatar_path="/static/images/default-avatar.png",
            bio="Стример и киберспортсмен",
            created_at=datetime.utcnow() - timedelta(days=5),
            last_login=datetime.utcnow() - timedelta(hours=5)
        ),
        UserModel(
            username="Karrew9",
            email="maximzaripovs887@gmail.com",
            password_hash=hash_password("qwertyui"),  # Настоятельно рекомендую использовать более сложный пароль
            is_active=True,
            avatar_path="/static/images/default-avatar.png",
            bio="Разработчик этого блога и фанат игр",
            created_at=datetime.utcnow() - timedelta(days=0),
            last_login=datetime.utcnow()
        ),
        UserModel(
            username="ShadowMage777",
            email="shadow@example.com",
            password_hash=hash_password("ShadowMagic777"),
            is_active=True,
            avatar_path="/static/images/default-avatar.png",
            bio="Фанат RPG и фэнтези-игр",
            created_at=datetime.utcnow() - timedelta(days=15),
            last_login=datetime.utcnow() - timedelta(days=3)
        )
    ]
    session.add_all(users)
    session.commit()

    posts = [
        PostModel(
            title="Обзор Cyberpunk 2077: Phantom Liberty",
            content="После долгого ожидания наконец-то прошел дополнение Phantom Liberty для Cyberpunk 2077. CD Projekt RED проделали невероятную работу!\n\nНовый район Догтаун просто поражает своей атмосферой, а сюжетная линия с Соми и президентом Майерс держит в напряжении от начала до конца. Особенно впечатлили:\n- Новые способности\n- Переработанная система прокачки\n- Дополнительные концовки\n\nОптимизация тоже на высоте - игра работает стабильно даже на средних ПК.",
            author_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=3)
        ),
        PostModel(
            title="Топ-10 инди-игр 2024 года",
            content="Инди-сцена в этом году просто взорвалась! Вот мой личный топ: 1) Pizza Tower - безумный платформер с отличным саундтреком, 2) Blasphemous 2 - мрачная метроидвания с потрясающим артом, 3) Sea of Stars - ностальгическая JRPG с современной подачей. Каждая из этих игр доказывает, что для создания шедевра не нужен огромный бюджет. 4) Cocoon - минималистичная головоломка с гениальным дизайном уровней, 5) Venba - трогательная история об индийской семье, рассказанная через кулинарию, 6) Dredge - атмосферная рыбалка с элементами хоррора, 7) Moonstone Island - уютный симулятор жизни с покемонами, 8) Viewfinder - инновационная головоломка с фотографиями, 9) Jusant - медитативное скалолазание в постапокалипсисе, 10) Hogwarts Legacy - хоть и не совсем инди, но показала как нужно делать игры по франшизам.",
            author_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
        PostModel(
            title="Гайд по прохождению Elden Ring без урона",
            content="Привет, безумцы! Решил бросить себе вызов и пройти Elden Ring без единого полученного урона. После 147 попыток могу поделиться советами: 1) Изучите каждого босса досконально - их паттерны атак это ключ к победе, 2) Не жадничайте с ударами - лучше нанести один точный удар, чем получить в ответ, 3) Используйте окружение в свою пользу. Особенно сложными оказались Малекит и Малена. Для Малекита критически важно выучить тайминги его комбо во второй фазе. Малена требует идеального позиционирования и молниеносной реакции на ее Танец Водоплавающей Птицы. Обязательно используйте Пепел Войны 'Кровавый Шаг' для уклонения. Не забывайте про расходники - даже если не получаете урон, бафы значительно ускорят бой. И помните: терпение - ваш лучший друг в этом челлендже!",
            author_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        PostModel(
            title="Почему Baldur's Gate 3 - игра года",
            content="Larian Studios создали настоящий шедевр! Baldur's Gate 3 это не просто игра, это целая вселенная с невероятной свободой выбора. Каждое прохождение уникально, диалоги проработаны до мелочей, а количество вариантов развития событий просто поражает. Отдельно хочу отметить озвучку и анимацию персонажей - это новый стандарт для RPG. Романтические линии проработаны так глубоко, что каждый компаньон чувствуется живым человеком со своими проблемами и мотивацией. Боевая система на основе D&D 5e идеально адаптирована для видеоигры. Возможность решать квесты десятками разных способов делает каждое прохождение уникальным. А кооператив до 4 игроков превращает игру в настоящую настольную RPG-сессию. Это та игра, которая задает новую планку качества для всей индустрии!",
            author_id=users[3].id,
            created_at=datetime.utcnow() - timedelta(hours=12)
        ),
        PostModel(
            title="Ностальгия: вспоминаем классику PS1",
            content="Недавно достал свою старую PlayStation 1 и погрузился в ностальгию. Silent Hill до сих пор пугает своей атмосферой, Metal Gear Solid остается эталоном стелс-экшена, а Final Fantasy VII... эта игра изменила индустрию навсегда. Удивительно, как эти игры с их пиксельной графикой до сих пор вызывают больше эмоций, чем многие современные ААА-проекты. Crash Bandicoot научил нас, что платформеры могут быть хардкорными. Spyro the Dragon показал, как делать 3D-миры яркими и запоминающимися. Resident Evil 2 заложил основы современных хорроров. Gran Turismo стала первым настоящим автосимулятором на консолях. Tekken 3 до сих пор считается одним из лучших файтингов. Эти игры не просто развлекали - они формировали индустрию и наши вкусы. Может, пора достать старую консоль с чердака?",
            author_id=users[4].id,
            created_at=datetime.utcnow() - timedelta(days=4)
        ),
        PostModel(
            title="Сборка игрового ПК в 2024: мой опыт",
            content="Наконец-то собрал свой dream PC! Конфигурация: RTX 4080, Ryzen 9 7950X, 32GB DDR5. Теперь могу запускать Cyberpunk 2077 на ультрах с рейтрейсингом и получать стабильные 100+ FPS. Самое сложное было достать видеокарту по адекватной цене. Делюсь советами где искать комплектующие и как не переплатить. Материнская плата: ASUS ROG Strix X670E-A, охлаждение: be quiet! Dark Rock Pro 4, накопитель: Samsung 990 PRO 2TB. Блок питания не экономьте - взял Corsair RM1000x. Корпус Fractal Design Torrent обеспечивает отличный airflow. Общая стоимость вышла около 300к рублей, но оно того стоит! Советую следить за акциями в DNS и Ситилинке, использовать агрегаторы цен. И обязательно берите комплектующие с гарантией - это спасет нервы в случае брака.",
            author_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(hours=18)
        ),
        PostModel(
            title="История серии The Legend of Zelda",
            content="От 8-битной классики до Tears of the Kingdom - серия Zelda прошла невероятный путь. Каждая игра привносила что-то новое: Ocarina of Time показала как делать 3D-приключения, Wind Waker удивила cel-shaded графикой, а Breath of the Wild переосмыслила формулу открытого мира. Nintendo доказывают, что инновации важнее графики. Majora's Mask с её мрачной атмосферой и временной петлей опередила время. Twilight Princess вернула серию к реализму. Skyward Sword представила motion controls. A Link Between Worlds показала, что 2D-Zelda все еще актуальна. Но настоящая революция произошла с BotW - физический движок, химия элементов, полная свобода исследования. Tears of the Kingdom пошла еще дальше с системой крафта. Серия остается эталоном game-дизайна и доказательством, что геймплей важнее графики.",
            author_id=users[4].id,
            created_at=datetime.utcnow() - timedelta(days=5)
        ),
        PostModel(
            title="Мультиплеерные шутеры: что выбрать в 2025",
            content="CS2, Valorant, Overwatch 2, Apex Legends - выбор огромный! Каждая игра имеет свои особенности: CS2 - для олдскульных фанатов тактических шутеров, Valorant - микс CS и способностей героев, Overwatch 2 - командная игра с упором на синергию, Apex - королевская битва с уникальной системой передвижения. Разбираю плюсы и минусы каждой. CS2 получил новый движок Source 2, улучшенную физику дыма и переработанные карты, но коммьюнити токсичное. Valorant радует регулярными обновлениями и отличной античит-системой Vanguard, но требует много времени на изучение. Overwatch 2 перешел на F2P модель, добавил PvE режимы, но баланс хромает. Apex отличается высоким skill ceiling и динамичным геймплеем, но новичкам тяжело. Мой выбор - Valorant для соревновательной игры и Apex для фана с друзьями.",
            author_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(hours=8)
        ),
        PostModel(
            title="Лор Dark Souls: скрытые детали",
            content="Dark Souls славится своей загадочной подачей сюжета. После 500+ часов в игре нашел удивительные детали: знали ли вы, что Солер может быть сыном Гвина? Или что Праматерь Бездны была человеком? Каждый предмет, каждая локация рассказывает часть истории. FromSoftware создали настоящий шедевр сторителлинга через окружение. Описания предметов раскрывают трагедию Арториаса и его волка Сифа. Архитектура Анор Лондо намекает на величие угасающей эпохи богов. Сломанный меч в Пепельном Озере рассказывает о древних драконах. Даже расположение врагов не случайно - каждый полый рыцарь когда-то был героем. Музыка Мотои Сакурабы усиливает меланхоличную атмосферу умирающего мира. Dark Souls - это не просто сложная игра, это философское размышление о цикличности, жертвенности и неизбежности конца.",
            author_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(days=6)
        ),
        PostModel(
            title="Steam Deck изменил мой взгляд на портативный гейминг",
            content="Купил Steam Deck месяц назад и не могу оторваться! Возможность играть в свою библиотеку Steam где угодно - это невероятно. God of War в метро, Hades в обеденный перерыв, Stray перед сном. Производительность впечатляет, батарея держит 4-6 часов в зависимости от игры. Valve создали идеальное устройство для гиков. SteamOS на базе Linux работает стабильно, Proton позволяет запускать большинство Windows-игр. Можно установить эмуляторы и играть в классику от NES до PS3. Контроллеры удобные, тачпады открывают новые возможности управления. Док-станция превращает Deck в полноценный ПК. За эти деньги (около 60к рублей) это лучшее предложение на рынке. Nintendo Switch отдыхает! Единственный минус - размер и вес, но к этому быстро привыкаешь.",
            author_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(hours=3)
        )
    ]
    session.add_all(posts)
    session.commit()

    comments = [
        CommentModel(
            content="Полностью согласен! Phantom Liberty это то, каким должно быть DLC - полноценная история с новыми механиками.",
            author_id=users[1].id,
            post_id=posts[0].id,
            created_at=datetime.utcnow() - timedelta(hours=5)
        ),
        CommentModel(
            content="А я до сих пор жду оптимизацию для старых видеокарт... RTX 3060 еле тянет на средних.",
            author_id=users[3].id,
            post_id=posts[0].id,
            created_at=datetime.utcnow() - timedelta(hours=3)
        ),
        CommentModel(
            content="Pizza Tower это просто шедевр! Саундтрек слушаю каждый день.",
            author_id=users[0].id,
            post_id=posts[1].id,
            created_at=datetime.utcnow() - timedelta(hours=2)
        ),
        CommentModel(
            content="147 попыток?! Ты монстр! Я даже с уроном еле прошел...",
            author_id=users[4].id,
            post_id=posts[2].id,
            created_at=datetime.utcnow() - timedelta(minutes=45)
        ),
        CommentModel(
            content="Самое главное - терпение. У меня ушло 200+ попыток на Малению одну.",
            author_id=users[2].id,
            post_id=posts[2].id,
            created_at=datetime.utcnow() - timedelta(minutes=30)
        ),
        CommentModel(
            content="BG3 точно GOTY! 150 часов и я только в конце второго акта.",
            author_id=users[3].id,
            post_id=posts[3].id,
            created_at=datetime.utcnow() - timedelta(hours=1)
        ),
        CommentModel(
            content="Silent Hill на PS1 до сих пор страшнее многих современных хорроров!",
            author_id=users[3].id,
            post_id=posts[4].id,
            created_at=datetime.utcnow() - timedelta(hours=4)
        ),
        CommentModel(
            content="Сколько в итоге вышла сборка? Думаю тоже обновиться.",
            author_id=users[3].id,
            post_id=posts[5].id,
            created_at=datetime.utcnow() - timedelta(minutes=90)
        ),
        CommentModel(
            content="Breath of the Wild навсегда изменила open world игры. Жду что покажут в следующей части!",
            author_id=users[1].id,
            post_id=posts[6].id,
            created_at=datetime.utcnow() - timedelta(hours=6)
        ),
        CommentModel(
            content="Steam Deck лучшая покупка года! Особенно для командировок.",
            author_id=users[2].id,
            post_id=posts[9].id,
            created_at=datetime.utcnow() - timedelta(minutes=15)
        )
    ]
    session.add_all(comments)
    session.commit()

    print("База данных успешно заполнена тестовыми данными!")