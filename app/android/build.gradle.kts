allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir = file("C:/build_lang")
rootProject.layout.buildDirectory.set(newBuildDir)

subprojects {
    project.layout.buildDirectory.set(file("C:/build_lang/${project.name}"))
}
subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
