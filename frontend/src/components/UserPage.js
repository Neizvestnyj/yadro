import {Link, useParams, useSearchParams} from 'react-router-dom';
import {Button, Card, Spinner} from 'react-bootstrap';
import axios from 'axios';
import {useEffect, useState} from 'react';

/**
 * Компонент страницы пользователя.
 *
 * :returns: JSX-элемент страницы пользователя.
 * :rtype: JSX.Element
 */
const UserPage = () => {
    const {id} = useParams();
    const [searchParams] = useSearchParams();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Читаем fromPage из URL, по умолчанию 1
    const fromPage = searchParams.get('fromPage') || '1';

    /**
     * Загружает данные пользователя по ID.
     */
    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/v1/users/${id}`, {
                    timeout: 5000,
                });
                setUser(response.data);
            } catch (error) {
                console.error('Ошибка загрузки пользователя:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchUser();
    }, [id]);

    if (loading) {
        return <Spinner animation="border"/>;
    }

    if (!user) {
        return <div>Пользователь не найден</div>;
    }

    return (
        <div>
            <h1>Детали пользователя</h1>
            <Card style={{width: '18rem'}}>
                <Card.Img variant="top" src={user.picture}/>
                <Card.Body>
                    <Card.Title>
                        {user.first_name} {user.last_name}
                    </Card.Title>
                    <Card.Text>
                        <strong>Титул:</strong> {user.title}<br/>
                        <strong>Пол:</strong> {user.gender}<br/>
                        <strong>Email:</strong> {user.email}<br/>
                        <strong>Телефон:</strong> {user.phone}<br/>
                        <strong>Мобильный:</strong> {user.cell}<br/>
                        <strong>Адрес:</strong> {user.street_number} {user.street_name}, {user.city}, {user.state}, {user.country}, {user.postcode}<br/>
                        <strong>Координаты:</strong> Широта: {user.latitude}, Долгота: {user.longitude}<br/>
                        <strong>Часовой пояс:</strong> {user.timezone_offset}<br/>
                        <strong>Внешний ID:</strong> {user.external_id}<br/>
                        <strong>Имя пользователя:</strong> {user.username}<br/>
                        <strong>UUID:</strong> {user.uuid}<br/>
                        <strong>Дата рождения:</strong> {new Date(user.dob).toLocaleDateString()}<br/>
                        <strong>Дата регистрации:</strong> {new Date(user.registered_at).toLocaleDateString()}<br/>
                        <strong>Национальность:</strong> {user.nat}<br/>
                        <strong>ID:</strong> {user.id}<br/>
                        <strong>Создано:</strong> {new Date(user.created_at).toLocaleDateString()}
                    </Card.Text>
                    <Button as={Link} to={`/?page=${fromPage}`} variant="primary">
                        Назад на главную
                    </Button>
                </Card.Body>
            </Card>
        </div>
    );
};

export default UserPage;