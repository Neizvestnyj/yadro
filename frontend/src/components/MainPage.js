import {useEffect, useRef, useState} from 'react';
import axios from 'axios';
import {Button, Form, Pagination, Spinner, Table} from 'react-bootstrap';
import {Link, useNavigate} from 'react-router-dom';

/**
 * Компонент главной страницы для загрузки и отображения пользователей с динамической пагинацией.
 *
 * :returns: JSX элемент главной страницы.
 * :rtype: JSX.Element
 */
const MainPage = () => {
    const [count, setCount] = useState('');
    const [users, setUsers] = useState([]); // Буфер всех загруженных пользователей
    const [page, setPage] = useState(1); // Текущая страница
    const [isFetching, setIsFetching] = useState(false); // Статус запроса новых пользователей
    const [isLoadingMore, setIsLoadingMore] = useState(false); // Статус фоновой загрузки
    const [hasMore, setHasMore] = useState(true); // Есть ли ещё данные
    const limit = 10; // Записей на странице
    const bufferSize = 200; // Целевой размер буфера
    const fetchSize = 50; // Размер одного запроса
    const navigate = useNavigate();
    const fetchTimeoutRef = useRef(null); // Для управления фоновыми запросами

    /**
     * Загружает пользователей с указанным смещением.
     *
     * :param offset: Смещение для запроса.
     * :type offset: number
     * :returns: Массив пользователей.
     * :rtype: Array
     */
    const fetchUsers = async (offset) => {
        console.log(`Fetching users with offset=${offset}, limit=${fetchSize}`);
        try {
            const response = await axios.get(`http://localhost:8000/v1/users?limit=${fetchSize}&offset=${offset}`);
            console.log(`Fetched ${response.data.length} users`);
            return response.data;
        } catch (error) {
            console.error('Error fetching users:', error);
            return [];
        }
    };

    /**
     * Запрашивает новые записи, если буфер недостаточен.
     */
    const loadMoreUsers = async () => {
        if (!hasMore || isLoadingMore) {
            console.log('Skipping loadMoreUsers:', {hasMore, isLoadingMore, usersLength: users.length});
            return;
        }
        setIsLoadingMore(true);
        const offset = users.length;
        const newUsers = await fetchUsers(offset);
        if (newUsers.length < fetchSize) {
            setHasMore(false); // Данные закончились
            console.log('No more data available');
        }
        setUsers((prev) => [...prev, ...newUsers]);
        setIsLoadingMore(false);
    };

    /**
     * Отправляет запрос на загрузку новых пользователей из API.
     */
    const handleFetchUsers = async () => {
        if (!count || count <= 0) return;
        setIsFetching(true);
        try {
            await axios.post(`http://localhost:8000/v1/users/fetch?count=${count}`);
            setUsers([]); // Очищаем буфер
            setPage(1);
            setHasMore(true);
            const newUsers = await fetchUsers(0);
            setUsers(newUsers);
            if (newUsers.length < fetchSize) {
                setHasMore(false);
            }
            console.log('Initialized with', newUsers.length, 'users');
        } catch (error) {
            console.error('Error fetching users from API:', error);
        } finally {
            setIsFetching(false);
        }
    };

    /**
     * Переходит на страницу случайного пользователя.
     */
    const handleGetRandomUser = async () => {
        navigate('/random');
    };

    /**
     * Проверяет необходимость загрузки данных для текущей страницы и в фоне.
     */
    useEffect(() => {
        if (fetchTimeoutRef.current) {
            clearTimeout(fetchTimeoutRef.current);
        }
        console.log('Current state:', {page, usersLength: users.length, hasMore});

        // Принудительная загрузка, если данных для текущей страницы нет
        if (users.length < page * limit && hasMore) {
            console.log('Immediate loadMoreUsers for page', page);
            loadMoreUsers();
        }
        // Фоновая загрузка, если буфер мал
        else if (users.length - page * limit < bufferSize && hasMore) {
            console.log('Scheduling loadMoreUsers');
            fetchTimeoutRef.current = setTimeout(loadMoreUsers, 200); // Уменьшена задержка
        }

        return () => clearTimeout(fetchTimeoutRef.current);
    }, [page, users.length, hasMore]);

    /**
     * Инициализирует буфер при первом рендере.
     */
    useEffect(() => {
        const initializeUsers = async () => {
            if (users.length === 0) {
                const newUsers = await fetchUsers(0);
                setUsers(newUsers);
                if (newUsers.length < fetchSize) {
                    setHasMore(false);
                }
                console.log('Initialized with', newUsers.length, 'users');
            }
        };
        initializeUsers();
    }, []);

    /**
     * Генерирует элементы пагинации для отображения.
     *
     * :returns: Массив JSX элементов для пагинации.
     * :rtype: JSX.Element[]
     */
    const getPaginationItems = () => {
        const items = [];
        const maxPagesToShow = 5;
        const totalAvailablePages = Math.ceil(users.length / limit);
        const maxPage = hasMore ? Math.max(page + maxPagesToShow, totalAvailablePages) : totalAvailablePages;

        // Кнопка "в начало"
        items.push(
            <Pagination.Item
                key="first"
                disabled={page === 1}
                onClick={() => setPage(1)}
            >
                ««
            </Pagination.Item>
        );

        // Перемотка назад (на 5 страниц)
        items.push(
            <Pagination.Item
                key="rewind-back"
                disabled={page <= maxPagesToShow}
                onClick={() => setPage(Math.max(1, page - maxPagesToShow))}
            >
                «
            </Pagination.Item>
        );

        // Центральные страницы
        const startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
        const endPage = Math.min(maxPage, startPage + maxPagesToShow - 1);
        for (let i = startPage; i <= endPage; i++) {
            items.push(
                <Pagination.Item
                    key={i}
                    active={i === page}
                    onClick={() => setPage(i)}
                >
                    {i}
                </Pagination.Item>
            );
        }

        // Перемотка вперёд (на 5 страниц)
        if (hasMore || page + maxPagesToShow <= totalAvailablePages) {
            items.push(
                <Pagination.Item
                    key="rewind-forward"
                    onClick={() => setPage(page + maxPagesToShow)}
                >
                    »
                </Pagination.Item>
            );
        }

        return items;
    };

    // Текущая страница пользователей
    const currentPageUsers = users.slice((page - 1) * limit, page * limit);
    console.log('Rendering page', page, 'with', currentPageUsers.length, 'users');

    return (
        <div>
            <h1>Random User App</h1>
            <Form className="mb-4">
                <Form.Group className="mb-3">
                    <Form.Label>Number of users to fetch</Form.Label>
                    <Form.Control
                        type="number"
                        value={count}
                        onChange={(e) => setCount(e.target.value)}
                        placeholder="Enter number"
                        disabled={isFetching}
                    />
                </Form.Group>
                <Button
                    variant="primary"
                    onClick={handleFetchUsers}
                    className="me-2"
                    disabled={isFetching}
                >
                    {isFetching ? (
                        <>
                            <Spinner
                                as="span"
                                animation="border"
                                size="sm"
                                role="status"
                                aria-hidden="true"
                            />
                            {' Fetching...'}
                        </>
                    ) : (
                        'Fetch Users'
                    )}
                </Button>
                <Button variant="secondary" onClick={handleGetRandomUser} disabled={isFetching}>
                    Get Random User
                </Button>
            </Form>

            <Table striped bordered hover>
                <thead>
                <tr>
                    <th>Photo</th>
                    <th>Gender</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Location</th>
                    <th>Details</th>
                </tr>
                </thead>
                <tbody>
                {currentPageUsers.length === 0 ? (
                    <tr>
                        <td colSpan="8">
                            {isLoadingMore ? (
                                <>
                                    <Spinner animation="border" size="sm"/> Loading users...
                                </>
                            ) : (
                                'No users available for this page'
                            )}
                        </td>
                    </tr>
                ) : (
                    currentPageUsers.map((user) => (
                        <tr key={user.id}>
                            <td>
                                <img src={user.picture} alt="User" width="50"/>
                            </td>
                            <td>{user.gender}</td>
                            <td>{user.first_name}</td>
                            <td>{user.last_name}</td>
                            <td>{user.email}</td>
                            <td>{user.phone}</td>
                            <td>{user.location}</td>
                            <td>
                                <Link to={`/user/${user.id}`}>View</Link>
                            </td>
                        </tr>
                    ))
                )}
                </tbody>
            </Table>

            <Pagination className="justify-content-center">
                {getPaginationItems()}
            </Pagination>
        </div>
    );
};

export default MainPage;