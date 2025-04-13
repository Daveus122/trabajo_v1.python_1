from flask import Flask, request, render_template, redirect, flash
import time
import uuid

app = Flask(__name__)
app.secret_key = 'clave_secreta_simple'

# Lista para almacenar los recordatorios en memoria
reminders = []

@app.route("/api/reminders", methods=["GET"])
def index():
    sorted_reminders = sorted(reminders, key=lambda x: (-x['important'], x['createdAt']))
    return render_template("index.html", reminders=sorted_reminders)

# Ruta para crear un recordatorio (interfaz web)
@app.route("/api/reminders/create", methods=["POST"])
def create_reminder():
    content = request.form.get("content")
    important = request.form.get("important") == "on"

    # Validar content
    if not content or not isinstance(content, str) or not content.strip() or len(content.strip()) > 120:
        flash("El recordatorio debe ser un texto no vacío de máximo 120 caracteres", "error")
        return redirect("/api/reminders")

    new_reminder = {
        "id": str(uuid.uuid4()),
        "content": content.strip(),
        "createdAt": int(time.time() * 1000),
        "important": important
    }
    reminders.append(new_reminder)
    flash("Recordatorio creado", "success")
    return redirect("/api/reminders")

# Ruta para actualizar un recordatorio (interfaz web)
@app.route("/api/reminders/update/<string:id>", methods=["POST"])
def update_reminder(id):
    for reminder in reminders:
        if reminder["id"] == id:
            content = request.form.get("content")
            important = request.form.get("important") == "on"

            # Validar content
            if not content or not isinstance(content, str) or not content.strip() or len(content.strip()) > 120:
                flash("El recordatorio debe ser un texto no vacío de máximo 120 caracteres", "error")
                return redirect("/api/reminders")

            reminder["content"] = content.strip()
            reminder["important"] = important
            flash("Recordatorio actualizado", "success")
            return redirect("/api/reminders")
    flash("Recordatorio no encontrado", "error")
    return redirect("/api/reminders")

# Ruta para borrar un recordatorio (interfaz web)
@app.route("/api/reminders/delete/<string:id>", methods=["POST"])
def delete_reminder(id):
    for index, reminder in enumerate(reminders):
        if reminder["id"] == id:
            del reminders[index]
            flash("Recordatorio borrado", "success")
            return redirect("/api/reminders")
    flash("Recordatorio no encontrado", "error")
    return redirect("/api/reminders")

# API REST: Listar recordatorios
@app.route("/api/reminders/list", methods=["GET"])
def api_listar_reminders():
    sorted_reminders = sorted(reminders, key=lambda x: (-x['important'], x['createdAt']))
    return sorted_reminders, 200

# API REST: Crear un recordatorio
@app.route("/api/reminders", methods=["POST"])
def api_crear_reminder():
    datos = request.get_json()
    content = datos.get("content")
    important = datos.get("important", False)

    # Validar content
    if not content or not isinstance(content, str) or not content.strip() or len(content.strip()) > 120:
        return {"error": "El recordatorio debe ser un texto no vacío de máximo 120 caracteres"}, 400

    # Validar important
    if "important" in datos and not isinstance(important, bool):
        return {"error": "El campo 'important' debe ser un valor booleano"}, 400

    new_reminder = {
        "id": str(uuid.uuid4()),
        "content": content.strip(),
        "createdAt": int(time.time() * 1000),
        "important": important
    }
    reminders.append(new_reminder)
    return new_reminder, 201

# API REST: Actualizar un recordatorio
@app.route("/api/reminders/<string:id>", methods=["PATCH"])
def api_actualizar_reminder(id):
    for reminder in reminders:
        if reminder["id"] == id:
            datos = request.get_json()

            if "content" in datos:
                content = datos["content"]
                if not content or not isinstance(content, str) or not content.strip() or len(content.strip()) > 120:
                    return {"error": "El recordatorio debe ser un texto no vacío de máximo 120 caracteres"}, 400
                reminder["content"] = content.strip()

            if "important" in datos:
                if not isinstance(datos["important"], bool):
                    return {"error": "El campo 'important' debe ser un valor booleano"}, 400
                reminder["important"] = datos["important"]

            return reminder, 200
    return {"error": "Recordatorio no encontrado"}, 404

# API REST: Borrar un recordatorio
@app.route("/api/reminders/<string:id>", methods=["DELETE"])
def api_borrar_reminder(id):
    for index, reminder in enumerate(reminders):
        if reminder["id"] == id:
            del reminders[index]
            return '', 204
    return {"error": "Recordatorio no encontrado"}, 404

if __name__ == '__main__':
    app.run(debug=True)