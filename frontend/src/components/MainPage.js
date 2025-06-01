import {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import axios from 'axios';
import {Alert, Button, Form, Pagination, Spinner, Table} from 'react-bootstrap';
import {Link, useNavigate, useSearchParams} from 'react-router-dom';

/**
 * Компонент главной страницы для отображения пользователей с пагинацией.
 *
 * :returns: JSX-элемент главной страницы.
 * :rtype: JSX.Element
 */
const MainPage = () => {
    const [count, setCount] = useState('');
    const [users, setUsers] = useState(() => window.userCache?.users || []);
    const [searchParams, setSearchParams] = useSearchParams(); // setSearchParams стабильна
    const [page, setPage] = useState(() => {
        const pageParam = parseInt(searchParams.get('page'), 10);
        return pageParam > 0 ? pageParam : 1;
    });
    const [totalPages, setTotalPages] = useState(1);
    const [isFetching, setIsFetching] = useState(false);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [error, setError] = useState('');
    const limit = 10; // Константа в области видимости компонента, стабильна
    const bufferSize = 200; // Константа, стабильна
    const fetchSize = 50; // Константа, стабильна
    const navigate = useNavigate(); // navigate стабильна
    const fetchTimeoutRef = useRef(null);

    // Инициализация кеша, если его нет.
    // Использование window.userCache - это простой способ кеширования в памяти на стороне клиента.
    // Для более сложных сценариев рассмотрите React Context или Redux/Zustand.
    if (!window.userCache) {
        window.userCache = {users: []};
    }

    /**
     * Загружает пользователей с указанным смещением.
     */
    const fetchUsers = useCallback(async (offset) => {
        console.log(`Загрузка: offset=${offset}, limit=${fetchSize}`);
        try {
            const response = await axios.get(`http://localhost:8000/api/v1/users?limit=${fetchSize}&offset=${offset}`, {
                timeout: 5000,
            });
            console.log(`Загружено ${response.data.length} пользователей`);
            const totalUsersHeader = response.headers['x-total-count'];
            const parsedTotalUsers = totalUsersHeader ? parseInt(totalUsersHeader, 10) : NaN;

            if (!isNaN(parsedTotalUsers)) {
                setTotalPages(Math.ceil(parsedTotalUsers / limit));
            } else {
                // Если заголовок x-total-count отсутствует или некорректен,
                // можно попробовать обновить totalPages на основе текущих данных,
                // но это будет неточно для общей пагинации.
                console.warn("Заголовок x-total-count отсутствует или некорректен. TotalPages может быть неточным.");
                // Как вариант, если загружено меньше, чем fetchSize, предполагаем, что это последняя "порция" данных
                if (response.data.length < fetchSize) {
                    setTotalPages(Math.ceil((offset + response.data.length) / limit));
                }
            }
            return response.data;
        } catch (err) { // Изменено имя переменной ошибки для ясности
            console.error('Ошибка при загрузке пользователей:', err);
            setError('Ошибка при загрузке пользователей.');
            return [];
        }
    }, [fetchSize, limit]); // limit и fetchSize - константы, но для полноты можно указать

    /**
     * Загружает дополнительные пользователи.
     */
    const loadMoreUsers = useCallback(async () => {
        if (!hasMore || isLoadingMore) {
            console.log('Пропуск дополнительной загрузки:', {hasMore, isLoadingMore, usersLength: users.length});
            return;
        }
        setIsLoadingMore(true);
        const currentOffset = users.length; // Используем users.length для offset
        const newUsers = await fetchUsers(currentOffset); // fetchUsers теперь мемоизирован
        if (newUsers.length < fetchSize) { // fetchSize - константа
            setHasMore(false);
            console.log('Больше нет данных для загрузки');
        }
        setUsers((prevUsers) => {
            const updatedUsers = [...prevUsers, ...newUsers];
            window.userCache.users = updatedUsers; // Обновляем кеш
            return updatedUsers;
        });
        setIsLoadingMore(false);
    }, [hasMore, isLoadingMore, users.length, fetchUsers, fetchSize]); // users.length вместо users для более гранулярного контроля

    /**
     * Загружает новых пользователей из API (принудительно).
     */
    const handleFetchUsers = async () => {
        if (!count || parseInt(count, 10) <= 0) {
            setError('Количество должно быть больше 0');
            return;
        }
        setError('');
        setIsFetching(true);
        try {
            await axios.post(`http://localhost:8000/api/v1/users/fetch?count=${count}`);
            setUsers([]); // Очищаем текущих пользователей
            window.userCache.users = []; // Очищаем кеш
            setPage(1); // Сбрасываем на первую страницу
            setHasMore(true); // Сбрасываем флаг "есть еще"
            setSearchParams({page: '1'}); // Обновляем URL
            const newInitialUsers = await fetchUsers(0); // Загружаем первую порцию
            setUsers(newInitialUsers);
            window.userCache.users = newInitialUsers; // Обновляем кеш
            if (newInitialUsers.length < fetchSize) {
                setHasMore(false);
            }
            console.log('Инициализировано (handleFetchUsers):', newInitialUsers.length);
        } catch (err) {
            console.error('Ошибка API (handleFetchUsers):', err);
            setError('Ошибка загрузки из API.');
        } finally {
            setIsFetching(false);
        }
    };

    /**
     * Переходит на случайного пользователя.
     */
    const handleGetRandomUser = async () => {
        navigate('/random');
    };

    /**
     * Очищает ошибку при изменении count.
     */
    useEffect(() => {
        setError('');
    }, [count]);

    /**
     * Инициализирует буфер пользователей при первом рендере, если он пуст.
     */
    useEffect(() => {
        const initializeUsers = async () => {
            if (users.length === 0 && (!window.userCache || window.userCache.users.length === 0)) {
                console.log('Инициализация пользователей при первом запуске...');
                const initialNewUsers = await fetchUsers(0);
                setUsers(initialNewUsers);
                window.userCache.users = initialNewUsers;
                if (initialNewUsers.length < fetchSize) {
                    setHasMore(false);
                }
                console.log('Инициализировано (useEffect init):', initialNewUsers.length);
            }
        };
        initializeUsers();
    }, [users.length, fetchUsers, fetchSize]); // fetchUsers и fetchSize добавлены как зависимости

    /**
     * Проверяет необходимость загрузки дополнительных пользователей при изменении страницы или других зависимостей,
     * и обновляет URL.
     */
    useEffect(() => {
        // Очищаем предыдущий таймаут, если он был
        if (fetchTimeoutRef.current) {
            clearTimeout(fetchTimeoutRef.current);
            // fetchTimeoutRef.current = null; // Можно обнулить ref после очистки
        }
        console.log('Состояние для загрузки/буфера:', {page, usersLength: users.length, hasMore});

        setSearchParams({page: page.toString()});

        const requiredUsersForCurrentPage = page * limit;
        // Условие для загрузки, если текущих пользователей не хватает для текущей страницы
        if (users.length < requiredUsersForCurrentPage && hasMore) {
            console.log('Загрузка для текущей страницы', page);
            loadMoreUsers();
            // Условие для загрузки в буфер, если пользователей достаточно для текущей страницы,
            // но в "хвосте" буфера осталось мало
        } else if (users.length > 0 && (users.length - requiredUsersForCurrentPage) < bufferSize && hasMore) {
            console.log('Загрузка для буфера');
            loadMoreUsers();
        }

        // Захватываем сам объект ref для использования в функции очистки
        const capturedFetchTimeoutRef = fetchTimeoutRef;
        return () => {
            // Очищаем таймаут при размонтировании или перед следующим запуском эффекта
            if (capturedFetchTimeoutRef.current) {
                clearTimeout(capturedFetchTimeoutRef.current);
            }
        };
    }, [page, users.length, hasMore, loadMoreUsers, setSearchParams, limit, bufferSize]); // Все зависимости перечислены

    /**
     * Создаёт элементы пагинации.
     */
    const getPaginationItems = () => {
        const items = [];
        const maxPagesToShow = 5; // Количество отображаемых кнопок страниц (кроме первой/последней/перемоток)

        // Определяем максимальную страницу на основе totalPages или фактически загруженных данных
        const currentLoadedMaxPage = users.length > 0 ? Math.ceil(users.length / limit) : 1;
        const maxPage = Math.max(totalPages, currentLoadedMaxPage, 1); // Убедимся, что maxPage как минимум 1

        // Кнопка "в начало"
        items.push(
            <Pagination.Item key="first" disabled={page === 1} onClick={() => setPage(1)}>
                ««
            </Pagination.Item>
        );
        // Кнопка "назад на N страниц"
        items.push(
            <Pagination.Item
                key="rewind-back"
                disabled={page <= 1} // Неактивна, если на первой странице
                onClick={() => setPage(Math.max(1, page - maxPagesToShow))}
            >
                «
            </Pagination.Item>
        );

        // Расчет начальной и конечной страницы для отображения
        let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(maxPage, startPage + maxPagesToShow - 1);

        // Корректировка, если endPage слишком мал из-за близости к maxPage
        if (endPage - startPage + 1 < maxPagesToShow && startPage > 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            items.push(
                <Pagination.Item key={i} active={i === page} onClick={() => setPage(i)}>
                    {i}
                </Pagination.Item>
            );
        }

        // Кнопка "вперёд на N страниц"
        items.push(
            <Pagination.Item
                key="rewind-forward"
                disabled={page >= maxPage} // Неактивна, если на последней странице
                onClick={() => setPage(Math.min(maxPage, page + maxPagesToShow))}
            >
                »
            </Pagination.Item>
        );
        // Кнопка "в конец"
        items.push(
            <Pagination.Item key="last" disabled={page === maxPage} onClick={() => setPage(maxPage)}>
                »»
            </Pagination.Item>
        );
        return items;
    };

    const currentPageUsers = useMemo(
        () => users.slice((page - 1) * limit, page * limit),
        [users, page, limit] // limit добавлен как зависимость
    );
    console.log('Рендер страницы', page, 'отображается', currentPageUsers.length, 'пользователей из', users.length, 'всего');

    return (
        <div>
            <h1>Приложение Random User</h1>
            {error && (
                <Alert variant="danger" onClose={() => setError('')} dismissible>
                    {error}
                </Alert>
            )}
            <Form className="mb-4">
                <Form.Group className="mb-3">
                    <Form.Label>Количество пользователей для загрузки в БД</Form.Label>
                    <Form.Control
                        type="number"
                        value={count}
                        onChange={(e) => setCount(e.target.value)}
                        placeholder="Введите число"
                        disabled={isFetching}
                    />
                </Form.Group>
                <Button variant="primary" onClick={handleFetchUsers} className="me-2" disabled={isFetching}>
                    {isFetching ? (
                        <>
                            <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true"/>
                            {' Загрузка в БД...'}
                        </>
                    ) : (
                        'Загрузить в БД'
                    )}
                </Button>
                <Button variant="secondary" onClick={handleGetRandomUser} disabled={isFetching || isLoadingMore}>
                    Случайный пользователь
                </Button>
            </Form>

            <Table striped bordered hover responsive>
                <thead>
                <tr>
                    <th>Фото</th>
                    <th>Пол</th>
                    <th>Имя</th>
                    <th>Фамилия</th>
                    <th>Email</th>
                    <th>Телефон</th>
                    <th>Местоположение</th>
                    <th>Детали</th>
                </tr>
                </thead>
                <tbody>
                {currentPageUsers.length === 0 ? (
                    <tr>
                        <td colSpan="8" className="text-center">
                            {isFetching || isLoadingMore ? (
                                <>
                                    <Spinner animation="border" size="sm"/> Загрузка списка...
                                </>
                            ) : (
                                users.length > 0 ? 'Нет пользователей на этой странице' : 'Нет пользователей для отображения'
                            )}
                        </td>
                    </tr>
                ) : (
                    currentPageUsers.map((user) => (
                        <tr key={user.id}>
                            <td>
                                <img src={user.picture} alt={`${user.first_name} ${user.last_name}`} width="50"
                                     style={{borderRadius: '50%'}}/>
                            </td>
                            <td>{user.gender}</td>
                            <td>{user.first_name}</td>
                            <td>{user.last_name}</td>
                            <td>{user.email}</td>
                            <td>{user.phone}</td>
                            <td>{`${user.street_number || ''} ${user.street_name || ''}`.trim()}, {user.city}, {user.state}, {user.country}, {user.postcode}</td>
                            <td>
                                <Link
                                    to={`/user/${user.id}?fromPage=${page}`}
                                    style={{textDecoration: 'none'}}
                                >
                                    Просмотр
                                </Link>
                            </td>
                        </tr>
                    ))
                )}
                </tbody>
            </Table>

            {/* Показываем пагинацию, только если есть что пагинировать */}
            {(users.length > 0 || totalPages > 1) && (
                <div className="d-flex justify-content-center">
                    <Pagination>{getPaginationItems()}</Pagination>
                </div>
            )}

            {isLoadingMore && (
                <div className="text-center my-3">
                    <Spinner animation="border" size="sm"/> Загрузка дополнительных пользователей...
                </div>
            )}
        </div>
    );
};

export default MainPage;