from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from .models import Database
from datetime import date, time, datetime, timedelta
from .aux_shows import *
from .molinete import *
from .manageJson import agregarElementoJson, agregarIterableJson
import json


# def home(request):
#     try:
#         user_id = request.session["user_id"]
#         return render(request, "home.html", {"user_id":True})
#     except:
#         return render(request, "home.html")


# def cartelera(request):
#     return render(request, "cartelera.html")


def esAdmin(request):
        try:
            user_admin = request.session["user_admin"]
            return user_admin == 1
        except:
            return False


def cartelera(request, user_id):

        db=Database()
        fechaHoraActual = datetime.now()
        info=db.cartelera(fechaHoraActual)
        generos=db.all_genres()
        admin = esAdmin(request)
        return render(request, "cartelera.html", {"peliculas": info, "user_id":user_id, "generos":generos, "titulo":"Cartelera", "user_admin":admin})



def mostrarFunciones(request):
        peliculaId=request.POST.get("peliculaId")

        db=Database()
        fechaActual = datetime.now()
        peliculaShows = db.movie_show_by_id(peliculaId, fechaActual)
        pelicula = db.movie_by_id(peliculaId)
        generos=db.all_genres()

        admin = esAdmin(request)
        
        return render(request, "movie-show.html",{ "pelicula":pelicula, "user_id":True, "titulo": "Elegir Función", "shows":peliculaShows, "generos":generos, "user_admin":admin})




def estrenos(request, user_id):
    db=Database()
    fechaHoraActual = datetime.now()
    info=db.estrenos(fechaHoraActual)
    generos=db.all_genres()
    admin = esAdmin(request)

    return render(request, "cartelera.html", {"peliculas": info, "user_id":user_id, "generos":generos, "titulo":"Próximos Estrenos", "user_admin":admin})


def agregarPelicula(request):
    db=Database()
    info=db.all_genres()

    return render(request, "form-movie.html", {"info":info, "user_id":True, "user_admin":True})

def seleccionarPelicula (request):
    
    if request.method == "POST": #Si entra por POST
        movieId=request.POST.get("movieId")
        db = Database()
        pelicula = db.movie_by_id(movieId)
        genero = db.all_genres()
        fecha_estreno = datetime.strftime(pelicula[8], '%Y-%m-%d')
        print(pelicula)
        return render(request, "form-edit-movie.html", { "info":pelicula, "generos":genero,"fecha_estreno":fecha_estreno, "user_id":True, "user_admin":True})
    else:
        db=Database()
        info=db.all_movies()

        rutaForm = "/admin/editar/pelicula/"
        return render(request, "form-select-movie.html", {"info":info, "rutaForm": rutaForm ,"user_id":True , "boton":["btn-primary", "Seleccionar"], "user_admin":True})


def seleccionarFuncionMolinete(request):
    db=Database()
    if request.method == "POST": #Si entra por POST
        showId=request.POST.get("showId")
        entradas = db.entradas_by_show_id(showId)
        cantidad_entradas = len(entradas)
        print(cantidad_entradas)
        return render(request, "molinete.html", {"cantidad_entradas":cantidad_entradas, "user_id":True, "formClass":"","msg":"d-none", "user_admin":True})
    else:
        today = date.today()
        db=Database()
        print(today)
        info=db.show_by_date_movie_title(str(today))
        print(info)
        rutaForm = "/admin/molinete/"
        return render(request, "form-select-show-molinete.html", {"info":info, "rutaForm": rutaForm ,"user_id":True, "boton":["btn-primary", "Seleccionar"], "user_admin":True})


def eliminarPelicula(request):
    db=Database()

    if request.method == "POST": #Si entra por POST
        movieId=request.POST.get("movieId")
        shows = db.show_by_movie_id(movieId)

        agregarIterableJson('funciones', shows)
        agregarElementoJson('peliculas', str(db.movie_by_id(movieId)))
        agregarIterableJson('entradas', db.entradas_by_movie_id(movieId))

        for show in shows:
            db.delete_entradas_by_show(show[0])
        
        db.delete_show_by_movie(movieId)
        db.delete_movie(movieId)



        return redirect("/admin/")
    else:

        info=db.all_movies()

        rutaForm = "/admin/eliminar/pelicula/"
        return render(request, "form-select-movie.html", {"info":info, "rutaForm": rutaForm ,"user_id":True, "boton":["btn-danger", "Eliminar"], "user_admin":True})


def editandoPelicula(request):

    movieId = request.POST.get("movieId")
    db=Database()

    if request.method == "POST": #Si entra por POST

        titulo=request.POST.get("titulo")
        duracion=request.POST.get("duracion")
        calificacion=request.POST.get("calificacion")
        imagenLink=request.POST.get("imagenLink")
        idioma=request.POST.get("idioma")
        genero=request.POST.get("genero")
        resenia=request.POST.get("resenia")
        fechaEstreno=request.POST.get("date")
        db.update_movie(movieId, titulo, resenia, duracion, calificacion, idioma, genero, imagenLink, fechaEstreno)
        return redirect("/admin/")




def agregarFuncion(request):
    if request.method == "POST": #Si entra por POST
        peliculaId=request.POST.get("peliculaId")
        salaId=request.POST.get("salaId")
        date=request.POST.get("date")
        time=request.POST.get("time")
        precio=request.POST.get("precio")

        #Convertir a datetime
        fechaConcatenada = date + " " + time
        fecha_dt = datetime.strptime(fechaConcatenada, '%Y-%m-%d %H:%M:00')

        db=Database()
        db.insert_show(peliculaId, salaId, fecha_dt, precio)

        #Hacer que redireccione a la pagina de panel de administrador
        movies=db.all_movies()
        rooms=db.all_rooms()
        fechaHoraActual = datetime.now()

        lunesAnterior = primerLunesAnterior(fechaHoraActual)
        lunesSiguiente = lunesAnterior + timedelta(days=7)
        matrizSemana1 = matriz_shows_semana(lunesAnterior)
        matrizSemana2 = matriz_shows_semana(lunesSiguiente)
        dias = proximosDias(lunesAnterior, 14)


        return render(request, "form-show.html", {"movies":movies, "rooms":rooms, "user_id":True, "matrizSemana1":matrizSemana1, "matrizSemana2":matrizSemana2, "dias":dias, "user_admin":True })

    else:
        db=Database()
        movies=db.all_movies()
        rooms=db.all_rooms()

        fechaHoraActual = datetime.now()

        lunesAnterior = primerLunesAnterior(fechaHoraActual)
        lunesSiguiente = lunesAnterior + timedelta(days=7)
        matrizSemana1 = matriz_shows_semana(lunesAnterior)
        matrizSemana2 = matriz_shows_semana(lunesSiguiente)
        dias = proximosDias(lunesAnterior, 14)

        return render(request, "form-show.html", {"movies":movies, "rooms":rooms, "user_id":True, "matrizSemana1":matrizSemana1, "matrizSemana2":matrizSemana2, "dias":dias, "user_admin":True })

def seleccionarFuncion (request):
    if request.method == "POST": #Si entra por POST
        showId=request.POST.get("showId")
        db = Database()
        funcion = db.show_by_id(showId)
        #peliculaId = db.movie_by_show_id(showId)
        #pelicula = db.movie_by_id(peliculaId)
        fecha = datetime.strftime(funcion[1], '%Y-%m-%d')
        hora = datetime.strftime(funcion[1], '%H:%M:%S')
        movies=db.all_movies()
        rooms=db.all_rooms()

        fechaHoraActual = datetime.now()

        lunesAnterior = primerLunesAnterior(fechaHoraActual)
        lunesSiguiente = lunesAnterior + timedelta(days=7)
        matrizSemana1 = matriz_shows_semana(lunesAnterior)
        matrizSemana2 = matriz_shows_semana(lunesSiguiente)
        dias = proximosDias(lunesAnterior, 14)

        return render(request, "form-edit-show.html", {"funcion":funcion, "fecha":fecha, "hora":hora, "movies":movies, "rooms":rooms, "user_id":True, "matrizSemana1":matrizSemana1, "matrizSemana2":matrizSemana2, "dias":dias, "user_admin":True })
    else:
        db=Database()
        info=db.all_shows()
        rutaForm = "/admin/editar/funcion/"
        return render(request, "form-select-show.html", {"info":info, "rutaForm": rutaForm ,"user_id":True , "boton":["btn-primary", "Seleccionar"], "user_admin":True})

def editandoFuncion (request):
    if request.method == "POST": #Si entra por POST
        peliculaId=request.POST.get("peliculaId")
        showId=request.POST.get("showId")
        salaId=request.POST.get("salaId")
        date=request.POST.get("date")
        time=request.POST.get("time")
        precio=request.POST.get("precio")

        #Convertir a datetime
        fechaConcatenada = date + " " + time
        fecha_dt = datetime.strptime(fechaConcatenada, '%Y-%m-%d %H:%M:00')

        db=Database()
        db.update_show(showId, fecha_dt, salaId, peliculaId, precio)
    
        return redirect("/admin/")

def eliminarFuncion (request):
    db = Database()
    if request.method == "POST": #Si entra por POST
        showId=request.POST.get("showId")

        agregarElementoJson('funciones', str(db.show_by_id(showId)))
        agregarIterableJson('entradas', db.entradas_by_show_id(showId))

        db.delete_entradas_by_show(showId)
        db.delete_show(showId)
        return redirect("/admin/")

    else:
        info=db.all_shows()
        rutaForm = "/admin/eliminar/funcion/"
        return render(request, "form-select-show.html", {"info":info, "rutaForm": rutaForm ,"user_id":True, "boton":["btn-danger", "Eliminar"], "user_admin":True})

def recibiendoPeliculaNueva(request):
    # if request.method == "POST":   anidar?

    titulo=request.POST.get("titulo")
    duracion=request.POST.get("duracion")
    calificacion=request.POST.get("calificacion")
    imagenLink=request.POST.get("imagenLink")
    idioma=request.POST.get("idioma")
    genero=request.POST.get("genero")
    resenia=request.POST.get("resenia")
    fechaEstreno=request.POST.get("date")


    db=Database()
    db.insert_movie(titulo, duracion, calificacion, imagenLink, idioma, genero, resenia, fechaEstreno)

    return render(request, "home.html")


####################### USUARIOS
def login(request):
    if request.method == "POST": #Si entra por POST
        email=request.POST.get("email")
        password=request.POST.get("password")

        db=Database()
        info=db.login(email, password)

        if info:
            request.session["user_id"] = info[0]
            request.session["user_admin"] = info[5]
            if info[5] == 1:
                return redirect("/admin")
            else:
                return redirect("/")
        else:
            return render(request, "login.html")

    else: #Si entra por GET
        try:
            user_id = request.session["user_id"]
            return redirect("/")
        except:
            return render(request, "login.html")



def register(request):
    if request.method == "POST": #Si entra por POST
        usuario=request.POST.get("usuario")
        fecha_nacimiento=request.POST.get("fecha_nacimiento")
        email=request.POST.get("email")
        password=request.POST.get("password")

        db=Database()
        db.insert_user(usuario, fecha_nacimiento, email, password)

        return render(request, "login.html")

    else: #Si entra por GET
        return render(request, "register.html")



def userEdit(request):
    user_id = request.session["user_id"]
    db=Database()
    user=db.user_by_id(user_id)
    admin = esAdmin(request)

    if request.method == "POST": #Si entra por POST
        usuario=request.POST.get("usuario")
        fecha_nacimiento=request.POST.get("fecha_nacimiento")
        email=request.POST.get("email")
        password=request.POST.get("password")

        if password == "":
            password = user[2]

        db.update_user(usuario, fecha_nacimiento, email, password, user_id)
        return redirect("/")

    else: #Si entra por GET
        db=Database()
        user=db.user_by_id(user_id)
        fecha_nacimiento = datetime.strftime(user[4], '%Y-%m-%d')

        return render(request, "user-edit.html", {"user_id":True, "user":user, "fecha_nacimiento":fecha_nacimiento, "user_admin":admin})
        


def userDelete(request):
    user_id = request.session["user_id"]
    db=Database()
    db.delete_user(user_id)
    return redirect("/cerrarsesion/")



def mostrarButacas(request):
    if request.method == "POST":
        db=Database()
        show_id=request.POST.get("show_id")
        show=db.show_by_id(show_id)
        entradas = db.entradas_by_show_id(show_id)
        butacasOcupadas = []
        for i in range(100):
            butacasOcupadas.append(False)
        for entrada in entradas:
            butacasOcupadas[entrada[3]-1] = True

        admin = esAdmin(request)

    return render(request, "compra.html", { "user_id":True, "butacasOcupadas":butacasOcupadas, "show_id":show_id, "precio":show[4], "user_admin":admin})







def entrada(request):
    db=Database()
    user_id = request.session["user_id"]
    fechaHoraActual = datetime.now()
    admin = esAdmin(request)

    if request.method == "POST":
        butacas=request.POST.get("butacas")
        show_id=request.POST.get("show_id")
        arr = butacas.replace('[', '').replace(']', '').split(',')
        show = db.show_by_id(show_id)
        precio = show[4]

        for butaca in arr:
            db.crearEntrada(show_id, user_id, butaca, precio)

        tickets = db.tickets_by_user(user_id, fechaHoraActual)
        return render(request, "tickets.html", { "user_id":True, "tickets":tickets, "user_admin":admin})

    else:
        tickets = db.tickets_by_user(user_id, fechaHoraActual)
        return render(request, "tickets.html", { "user_id":True, "tickets":tickets, "user_admin":admin})













def cerrarsesion(request):
    del request.session['user_id']
    del request.session['user_admin']
    return redirect("/")


# def auth_required(request, **kwargs):
#     try:
#         funcion = kwargs["funcion"]
#         user_id = request.session["user_id"]
#         return funcion(request)

#     except:
#         return redirect("/login")





def auth_required_pro(request, **kwargs):

    auth = kwargs["auth"]

    if auth == "user":
        try:
            user_id = request.session["user_id"]
            funcion = kwargs["funcion"]
            return funcion(request)
        except:
            return redirect("/login")

    elif auth == "admin":
        try:
            db=Database()
            info=db.isAdmin(request.session["user_id"])
            if info:
                funcion = kwargs["funcion"]
                return funcion(request)
            return redirect("/") #aca se podria hacer un HTML que diga que no tiene permisos
        except:
            return redirect("/login")

    elif auth == "anybody":
        funcion = kwargs["funcion"]
        try:
            user_id = request.session["user_id"]
            return funcion(request, True)
        except:
            return funcion(request, False)

    elif auth == "anybodySimple":
        view = kwargs["view"]
        admin = esAdmin(request)
        try:
            user_id = request.session["user_id"]
            return render(request, view, {"user_id":True, "user_admin":admin})
        except:
            return render(request, view)
            
    elif auth == "notLogged":
        try:
            user_id = request.session["user_id"]
            return redirect("/")
        except:
            funcion = kwargs["funcion"]
            return funcion(request)

    # match auth:
    #     case "user":
    #         try:
    #             user_id = request.session["user_id"]
    #             funcion = kwargs["funcion"]
    #             return funcion(request)
    #         except:
    #             return redirect("/login")

    #     case "admin":
    #             try:
    #                 db=Database()
    #                 info=db.isAdmin(request.session["user_id"])
    #                 if info:
    #                     funcion = kwargs["funcion"]
    #                     return funcion(request)
    #                 return redirect("/") #aca se podria hacer un HTML que diga que no tiene permisos
    #             except:
    #                 return redirect("/login")

    #     case "anybody":
    #         funcion = kwargs["funcion"]
    #         try:
    #             user_id = request.session["user_id"]
    #             return funcion(request, True)
    #         except:
    #             return funcion(request, False)

    #     case "anybodySimple":
    #         view = kwargs["view"]
    #         admin = esAdmin(request)
    #         try:
    #             user_id = request.session["user_id"]
    #             return render(request, view, {"user_id":True, "user_admin":admin})
    #         except:
    #             return render(request, view)

    #     case "notLogged":
    #         try:
    #             user_id = request.session["user_id"]
    #             return redirect("/")
    #         except:
    #             funcion = kwargs["funcion"]
    #             return funcion(request)


def adminView(request):
    return render(request, "admin-side-panel.html", {"user_id":True, "user_admin":True})

