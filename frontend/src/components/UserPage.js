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
                const response = await axios.get(`http://localhost:8000/v1/users/${id}`, {
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
                        <strong>Пол:</strong> {user.gender}
                        <br/>
                        <strong>Email:</strong> {user.email}
                        <br/>
                        <strong>Телефон:</strong> {user.phone}
                        <br/>
                        <strong>Местоположение:</strong> {user.location}
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