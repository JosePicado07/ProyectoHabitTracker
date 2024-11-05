import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict, Optional
from config_py import REGION, USER_POOL_ID, CLIENT_ID, AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY

logger = logging.getLogger(__name__)


class CognitoAuth:
    def __init__(self):
        """
        Inicializa el cliente de Cognito usando las configuraciones globales.
        """
        self.USER_POOL_ID = USER_POOL_ID
        self.CLIENT_ID = CLIENT_ID
        self.REGION = REGION

        # Crear cliente de Cognito con credenciales explícitas
        self.client = boto3.client(
            'cognito-idp',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        self._id_token = None
        self._access_token = None
        self._refresh_token = None

    @property
    def id_token(self) -> Optional[str]:
        return self._id_token

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    def register(self, email: str) -> Dict:
        """
        Registra un nuevo usuario en Cognito. Cognito enviará un correo con la contraseña temporal.
        """
        try:
            response = self.client.admin_create_user(
                UserPoolId=self.USER_POOL_ID,  # Usar la constante
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ],
                DesiredDeliveryMediums=['EMAIL']
            )

            if response['User']['Username']:
                logger.info(f"Usuario {email} registrado exitosamente")
                return {
                    'status': 'SUCCESS',
                    'message': 'Se ha enviado un correo con las instrucciones para completar el registro'
                }
            else:
                logger.error("Error inesperado en el registro")
                return {
                    'status': 'ERROR',
                    'message': 'Error durante el registro'
                }

        except self.client.exceptions.UsernameExistsException:
            logger.warning(f"Intento de registro con email existente: {email}")
            return {
                'status': 'ERROR',
                'message': 'El email ya está registrado'
            }
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Error durante el registro: {str(e)}'
            }

    def login(self, username: str, password: str) -> Dict:
        """
        Inicia sesión del usuario usando Cognito.
        """
        try:
            response = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                },
                ClientId=self.CLIENT_ID  # Usar la constante
            )

            if 'ChallengeName' in response and response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                logger.info(f"Se requiere cambio de contraseña para usuario {username}")
                return {
                    'status': 'NEW_PASSWORD_REQUIRED',
                    'session': response.get('Session'),
                    'message': 'Se requiere cambiar la contraseña'
                }

            if 'AuthenticationResult' in response:
                auth_result = response['AuthenticationResult']
                self._id_token = auth_result.get('IdToken')
                self._access_token = auth_result.get('AccessToken')
                self._refresh_token = auth_result.get('RefreshToken')

                logger.info(f"Login exitoso para usuario {username}")
                return {
                    'status': 'SUCCESS',
                    'token': self._id_token
                }

        except self.client.exceptions.NotAuthorizedException:
            logger.warning(f"Intento de login fallido para usuario {username}")
            return {
                'status': 'ERROR',
                'message': 'Credenciales inválidas'
            }
        except self.client.exceptions.UserNotConfirmedException:
            logger.warning(f"Usuario no confirmado: {username}")
            return {
                'status': 'ERROR',
                'message': 'Usuario no confirmado'
            }
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Error durante el inicio de sesión: {str(e)}'
            }

    def change_password(self, username: str, session: str, new_password: str) -> Dict:
        """
        Cambia la contraseña cuando es requerido (primer inicio de sesión).
        """
        try:
            response = self.client.respond_to_auth_challenge(
                ClientId=self.CLIENT_ID,  # Usar la constante
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=session,
                ChallengeResponses={
                    'USERNAME': username,
                    'NEW_PASSWORD': new_password
                }
            )

            if 'AuthenticationResult' in response:
                auth_result = response['AuthenticationResult']
                self._id_token = auth_result.get('IdToken')
                self._access_token = auth_result.get('AccessToken')
                self._refresh_token = auth_result.get('RefreshToken')

                logger.info(f"Cambio de contraseña exitoso para usuario {username}")
                return {
                    'status': 'SUCCESS',
                    'token': self._id_token,
                    'message': 'Contraseña actualizada exitosamente'
                }

            return {
                'status': 'ERROR',
                'message': 'Error durante el cambio de contraseña'
            }

        except self.client.exceptions.InvalidPasswordException:
            logger.warning(f"Contraseña inválida para usuario {username}")
            return {
                'status': 'ERROR',
                'message': 'La nueva contraseña no cumple con los requisitos de seguridad'
            }
        except Exception as e:
            logger.error(f"Error en cambio de contraseña: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Error durante el cambio de contraseña: {str(e)}'
            }

    def refresh_session(self) -> Dict:
        """
        Refresca la sesión usando el refresh token.
        """
        if not self._refresh_token:
            logger.warning("Intento de refrescar sesión sin refresh token")
            return {
                'status': 'ERROR',
                'message': 'No hay sesión activa'
            }

        try:
            response = self.client.initiate_auth(
                ClientId=self.CLIENT_ID,  # Usar la constante
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': self._refresh_token
                }
            )

            auth_result = response.get('AuthenticationResult', {})
            self._id_token = auth_result.get('IdToken')
            self._access_token = auth_result.get('AccessToken')

            logger.info("Sesión refrescada exitosamente")
            return {
                'status': 'SUCCESS',
                'token': self._id_token
            }

        except Exception as e:
            logger.error(f"Error al refrescar sesión: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Error al refrescar la sesión: {str(e)}'
            }

    def logout(self) -> Dict:
        """
        Cierra la sesión del usuario.
        """
        try:
            if self._access_token:
                self.client.global_sign_out(
                    AccessToken=self._access_token
                )

            # Limpiar tokens
            self._id_token = None
            self._access_token = None
            self._refresh_token = None

            logger.info("Sesión cerrada exitosamente")
            return {
                'status': 'SUCCESS',
                'message': 'Sesión cerrada exitosamente'
            }

        except Exception as e:
            logger.error(f"Error en logout: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Error durante el cierre de sesión: {str(e)}'
            }