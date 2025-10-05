-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 05-10-2025 a las 10:25:55
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `nasa`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `documentos_exoplanetas`
--

CREATE TABLE `documentos_exoplanetas` (
  `id` int(11) NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `tipo_archivo` varchar(50) NOT NULL,
  `tamano_archivo` int(11) NOT NULL,
  `ruta_archivo` varchar(500) NOT NULL,
  `donador` varchar(100) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_subida` timestamp NOT NULL DEFAULT current_timestamp(),
  `consentimiento` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `documentos_exoplanetas`
--
ALTER TABLE `documentos_exoplanetas`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `documentos_exoplanetas`
--
ALTER TABLE `documentos_exoplanetas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
