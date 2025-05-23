import {useEffect, useMemo, useRef, useState} from 'react';
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
    const [searchParams, setSearchParams] = useSearchParams();
    const [page, setPage] = useState(() => {
        const pageParam = parseInt(searchParams.get('page'), 10);
        return pageParam > 0 ? pageParam : 1;
    });
    const [totalPages, setTotalPages] = useState(1);
    const [isFetching, setIsFetching] = useState(false);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [error, setError] = useState(''); // Состояние для ошибки
    const limit = 10;
    const bufferSize = 200;
    const fetchSize = 50;
    const navigate = useNavigate();
    const fetchTimeoutRef = useRef(null);

    if (!window.userCache) {
        window.userCache = {users: []};
    }

    /**
     * Загружает пользователей с указанным смещением.
     *
     * :param offset: Смещение.
     * :type offset: number
     * :returns: Массив пользователей.
     * :rtype: Array
     */
    const fetchUsers = async (offset) => {
        console.log(`Загрузка: offset=${offset}, limit=${fetchSize}`);
        try {
            const response = await axios.get(`http://localhost:8000/v1/users?limit=${fetchSize}&offset=${offset}`, {
                timeout: 5000,
            });
            console.log(`Загружено ${response.data.length} пользователей`);
            const totalUsers = parseInt(response.headers['x-total-count'], 10) || response.data.length;
            setTotalPages(Math.ceil(totalUsers / limit));
            return response.data;
        } catch (error) {
            console.error('Ошибка:', error);
            setError('Ошибка при загрузке пользователей. Попробуйте снова.');
            return [];
        }
    };

    /**
     * Загружает дополнительные пользователи.
     */
    const loadMoreUsers = async () => {
        if (!hasMore || isLoadingMore) {
            console.log('Пропуск:', {hasMore, isLoadingMore, usersLength: users.length});
            return;
        }
        setIsLoadingMore(true);
        const offset = users.length;
        const newUsers = await fetchUsers(offset);
        if (newUsers.length < fetchSize) {
            setHasMore(false);
            console.log('Данные закончились');
        }
        setUsers((prev) => {
            const updated = [...prev, ...newUsers];
            window.userCache.users = updated;
            return updated;
        });
        setIsLoadingMore(false);
    };

    /**
     * Загружает новых пользователей из API.
     */
    const handleFetchUsers = async () => {
        if (!count || parseInt(count, 10) <= 0) {
            setError('Количество пользователей должно быть больше 0');
            return;
        }
        setError(''); // Очищаем ошибку перед загрузкой
        setIsFetching(true);
        try {
            await axios.post(`http://localhost:8000/v1/users/fetch?count=${count}`);
            setUsers([]);
            window.userCache.users = [];
            setPage(1);
            setHasMore(true);
            setSearchParams({page: '1'});
            const newUsers = await fetchUsers(0);
            setUsers(newUsers);
            window.userCache.users = newUsers;
            if (newUsers.length < fetchSize) {
                setHasMore(false);
            }
            console.log('Инициализировано:', newUsers.length);
        } catch (error) {
            console.error('Ошибка API:', error);
            setError('Ошибка при загрузке пользователей из API. Попробуйте снова.');
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
     * Инициализирует буфер.
     */
    useEffect(() => {
        const initializeUsers = async () => {
            if (users.length === 0 && window.userCache.users.length === 0) {
                const newUsers = await fetchUsers(0);
                setUsers(newUsers);
                window.userCache.users = newUsers;
                if (newUsers.length < fetchSize) {
                    setHasMore(false);
                }
                console.log('Инициализировано:', newUsers.length);
            }
        };
        initializeUsers();
    }, []);

    /**
     * Проверяет необходимость загрузки и обновляет URL.
     */
    useEffect(() => {
        if (fetchTimeoutRef.current) {
            clearTimeout(fetchTimeoutRef.current);
        }
        console.log('Состояние:', {page, usersLength: users.length, hasMore});

        setSearchParams({page: page.toString()});

        if (users.length < page * limit && hasMore) {
            console.log('Загрузка для страницы', page);
            loadMoreUsers();
        } else if (users.length - page * limit < bufferSize && hasMore) {
            console.log('Загрузка для буфера');
            loadMoreUsers();
        }

        return () => clearTimeout(fetchTimeoutRef.current);
    }, [page, users.length, hasMore, setSearchParams]);

    /**
     * Создаёт элементы пагинации.
     *
     * :returns: Массив JSX-элементов.
     * :rtype: JSX.Element[]
     */
    const getPaginationItems = () => {
        const items = [];
        const maxPagesToShow = 5;
        const totalAvailablePages = Math.ceil(users.length / limit);
        const maxPage = hasMore ? Math.max(page + maxPagesToShow, totalAvailablePages) : totalPages;

        items.push(
            <Pagination.Item key="first" disabled={page === 1} onClick={() => setPage(1)}>
                ««
            </Pagination.Item>
        );

        items.push(
            <Pagination.Item
                key="rewind-back"
                disabled={page <= maxPagesToShow}
                onClick={() => setPage(Math.max(1, page - maxPagesToShow))}
            >
                «
            </Pagination.Item>
        );

        const startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
        const endPage = Math.min(maxPage, startPage + maxPagesToShow - 1);
        for (let i = startPage; i <= endPage; i++) {
            items.push(
                <Pagination.Item key={i} active={i === page} onClick={() => setPage(i)}>
                    {i}
                </Pagination.Item>
            );
        }

        if (hasMore || page + maxPagesToShow <= totalPages) {
            items.push(
                <Pagination.Item key="rewind-forward" onClick={() => setPage(page + maxPagesToShow)}>
                    »
                </Pagination.Item>
            );
        }

        return items;
    };

    const currentPageUsers = useMemo(
        () => users.slice((page - 1) * limit, page * limit),
        [users, page, limit]
    );
    console.log('Рендер страницы', page, 'с', currentPageUsers.length);

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
                    <Form.Label>Количество пользователей</Form.Label>
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
                            {' Загрузка...'}
                        </>
                    ) : (
                        'Загрузить'
                    )}
                </Button>
                <Button variant="secondary" onClick={handleGetRandomUser} disabled={isFetching}>
                    Случайный пользователь
                </Button>
            </Form>

            <Table striped bordered hover>
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
                        <td colSpan="8">
                            {isLoadingMore ? (
                                <>
                                    <Spinner animation="border" size="sm"/> Загрузка...
                                </>
                            ) : (
                                'Нет пользователей'
                            )}
                        </td>
                    </tr>
                ) : (
                    currentPageUsers.map((user) => (
                        <tr key={user.id}>
                            <td>
                                <img src={user.picture} alt="Пользователь" width="50"/>
                            </td>
                            <td>{user.gender}</td>
                            <td>{user.first_name}</td>
                            <td>{user.last_name}</td>
                            <td>{user.email}</td>
                            <td>{user.phone}</td>
                            <td>{user.street_number} {user.street_name}, {user.city}, {user.state}, {user.country}, {user.postcode}</td>
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

            <Pagination className="justify-content-center">{getPaginationItems()}</Pagination>
        </div>
    );
};

export default MainPage;